import logging
import time
from abc import ABC, abstractmethod
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from typing import List
from credentials import slack_bot_user_oauth_token, slack_app_level_token
from configuration import file_system_path
from file_system.file_manager import FileManager
from vector.chroma import retrieve_relevant_documents
from oai_assistants.query_assistant_from_documents import get_response_from_assistant
import os


# Abstract base class for Slack event handlers
class SlackEventHandler(ABC):
    @abstractmethod
    def handle(self, client: SocketModeClient, req: SocketModeRequest, web_client: WebClient, bot_user_id: str):
        pass


# Handler for messages sent in Slack channels
class ChannelMessageHandler(SlackEventHandler):
    processed_messages = set()  # To keep track of processed message IDs

    def handle(self, client: SocketModeClient, req: SocketModeRequest, web_client: WebClient, bot_user_id: str):
        # Acknowledge the event immediately
        client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))

        event = req.payload.get("event", {})
        message_id = event.get("client_msg_id")  # Unique identifier for each message

        # Check if the message is a retry and already processed
        if message_id in self.processed_messages:
            return

        try:
            if req.type == "events_api":
                if self.is_valid_message(event, bot_user_id):
                    text = event.get("text", "")
                    channel_id = event["channel"]

                    if "?" in text:
                        # Handle question message
                        self.answer_question(channel_id, text, event.get("ts"), web_client)
                    else:
                        # Handle non-question message
                        self.send_default_response(text, channel_id, event.get("ts"), web_client)

                    # Add the message ID to the processed set
                    self.processed_messages.add(message_id)

        except Exception as e:
            logging.error(f"Error processing event: {e}", exc_info=True)

    def is_valid_message(self, event, bot_user_id):
        """ Check if the event is a valid user message """
        return event.get("type") == "message" and "subtype" not in event and event.get("user") != bot_user_id

    def send_default_response(self, text, channel_id, thread_ts, web_client):
        """ Send a default response to a non-question message """
        response_message = f"I got a message from you saying \"{text}\""
        web_client.chat_postMessage(channel=channel_id, text=response_message, thread_ts=thread_ts)

    def answer_question(self, channel_id, question, message_id_to_reply_under, web_client):
        """ Handle a question message """
        file_name = f"{channel_id}_context.txt"
        context = self.fetch_recent_messages(channel_id, web_client)
        self.save_context_to_file(context, file_name)

        response_text = self.generate_response(question, file_name)
        print("*"*100)
        print(response_text)
        print("*"*100)
        # Send the extracted text as a response in Slack
        web_client.chat_postMessage(channel=channel_id, text=response_text, thread_ts=message_id_to_reply_under)

    def fetch_recent_messages(self, channel_id, web_client):
        """ Fetch recent messages for context """
        response = web_client.conversations_history(channel=channel_id, limit=100)
        return "\n".join([msg.get('text') for msg in response.get('messages', [])])

    def save_context_to_file(self, context, file_name):
        """ Save the fetched context to a file """
        with open(os.path.join(file_system_path, file_name), 'w') as file:
            file.write(context)

    def generate_response(self, question, file_name):
        """ Generate a response for a question """
        file_id = file_name[:-4]
        relevant_document_ids = retrieve_relevant_documents(question)
        relevant_document_ids.append(file_id)
        response_obj = get_response_from_assistant(question, relevant_document_ids)

        # Extract the text from the first assistant message
        response_text = "No valid response found."  # Default response
        for message in response_obj.data:
            if message.role == "assistant":
                response_text = message.content[0].text.value
                break  # Assuming you only need the first assistant message

        return response_text

# Handler for reactions added to messages
class ReactionHandler(SlackEventHandler):
    def handle(self, client: SocketModeClient, req: SocketModeRequest, web_client: WebClient, bot_user_id: str):
        if req.type == "events_api":
            event = req.payload.get("event", {})
            if event.get("type") == "reaction_added" and event.get("item_user") == bot_user_id:
                reaction = event.get("reaction")
                channel_id = event.get("item", {}).get("channel")
                message_ts = event.get("item", {}).get("ts")
                response_message = f"I saw a :{reaction}: reaction on my message with timestamp {message_ts}"
                web_client.chat_postMessage(channel=channel_id, text=response_message)


# Main SlackBot class to initialize and manage the bot
class SlackBot:
    def __init__(self, token: str, app_token: str, bot_user_id: str, event_handlers: List[SlackEventHandler]):
        self.web_client = WebClient(token=token)
        self.socket_mode_client = SocketModeClient(app_token=app_token, web_client=self.web_client)
        self.bot_user_id = bot_user_id
        self.event_handlers = event_handlers

    def start(self):
        from functools import partial
        for event_handler in self.event_handlers:
            event_handler_func = partial(event_handler.handle, web_client=self.web_client, bot_user_id=self.bot_user_id)
            self.socket_mode_client.socket_mode_request_listeners.append(event_handler_func)

        self.socket_mode_client.connect()
        try:
            while True:
                logging.debug("Bot is running...")
                time.sleep(10)
        except KeyboardInterrupt:
            logging.info("Bot stopped by the user")
        except Exception as e:
            logging.critical("Bot stopped due to an exception", exc_info=True)


# Start the bot if this script is run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot_user_id = "U069C17DCE5"  # Replace with your bot's actual user ID
    event_handlers = [ChannelMessageHandler(), ReactionHandler()]
    bot = SlackBot(slack_bot_user_oauth_token, slack_app_level_token, bot_user_id, event_handlers)
    bot.start()
