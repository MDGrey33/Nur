import logging
import time
from abc import ABC, abstractmethod
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from typing import List
from credentials import slack_bot_user_oauth_token, slack_app_level_token
from file_system.file_manager import FileManager
from vector.chroma import retrieve_relevant_documents
from oai_assistants.query_assistant_from_documents import get_response_from_assistant



# Abstract base class for Slack event handlers
class SlackEventHandler(ABC):
    @abstractmethod
    def handle(self, client: SocketModeClient, req: SocketModeRequest, web_client: WebClient, bot_user_id: str):
        pass


# Handler for messages sent in Slack channels
class ChannelMessageHandler(SlackEventHandler):
    def handle(self, client: SocketModeClient, req: SocketModeRequest, web_client: WebClient, bot_user_id: str):
        try:
            logging.debug(f"Received event: {req.payload}")
            if req.type == "events_api":
                event = req.payload.get("event", {})
                logging.info(f"Event details: {event}")

                # Ignore messages from the bot itself
                if event.get("type") == "message" and "subtype" not in event and event.get("user") != bot_user_id:
                    text = event.get("text", "")
                    channel_id = event["channel"]
                    logging.info(f"Message received: '{text}' in channel {channel_id}")

                    # Respond to the message
                    response_message = f"I got a message from you saying \"{text}\""
                    web_client.chat_postMessage(channel=channel_id, text=response_message)
                    logging.info(f"Sent response in channel {channel_id}")

                client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
        except Exception as e:
            logging.error(f"Error processing event: {e}", exc_info=True)


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
