# ./slack/channel_interaction_threads.py
import logging
import time
from abc import ABC, abstractmethod
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from typing import List
from credentials import slack_bot_user_oauth_token, slack_app_level_token
from configuration import bot_user_id
from slack.event_publisher import EventPublisher
from slack.event_consumer_threads import consume_events

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
print("imports completed successfully")
# Initialize EventPublisher instance
event_publisher = EventPublisher()


class SlackEventHandler(ABC):
    @abstractmethod
    def handle(self, client: SocketModeClient, req: SocketModeRequest, web_client: WebClient, bot_user_id: str):
        pass


class ChannelMessageHandler(SlackEventHandler):
    processed_messages = set()  # Tracks all processed message ts
    questions = {}  # Maps 'ts' of a question to its text

    def handle(self, client: SocketModeClient, req: SocketModeRequest, web_client: WebClient, bot_user_id: str):
        # Acknowledge the event immediately
        client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))

        event = req.payload.get("event", {})
        ts = event.get("ts", "")  # Unique 'ts' for each message
        text = event.get("text", "")
        user_id = event.get("user", "")
        thread_ts = event.get("thread_ts")  # 'thread_ts' if part of a thread
        channel = event.get("channel", "")  # ID of the channel where the message was sent

        logging.debug(f"Event received: {event}")

        # Skip processing if the message has already been processed
        if ts in self.processed_messages:
            logging.info(f"Message {ts} already processed. Skipping.")
            print(f"Message {ts} already processed. Skipping.")
            return

        # Update the processed_messages set with the 'ts'
        self.processed_messages.add(ts)

        # Determine the reason for skipping before the checks
        skip_reason = self.determine_skip_reason(event, ts, text, thread_ts, user_id, bot_user_id)

        # Skip if message is invalid or from the bot itself
        if not self.is_valid_message(event) or user_id == bot_user_id:
            logging.warning(f"Skipping message with ID {ts} from user {user_id}. Reason: {skip_reason}")
            print(f"Skipping message with ID {ts} from user {user_id}. Reason: {skip_reason}")
            return

        # Identify and handle questions
        if "?" in text and (not thread_ts):  # It's a question if not part of another thread
            print(f"Question identified: {text}")
            self.questions[ts] = text
            question_event = {
                "text": text,
                "ts": ts,
                "thread_ts": "",
                "channel": channel,
                "user": user_id
            }
            event_publisher.publish_new_question(question_event)
            print(f"Question published: {question_event}")


        # Identify and handle feedback
        elif thread_ts in self.questions:  # Message is a reply to a question
            parent_question = self.questions[thread_ts]
            print(f"Feedback identified for question '{parent_question}': {text}")
            feedback_event = {
                "text": text,
                "ts": ts,
                "thread_ts": thread_ts,
                "channel": channel,
                "user": user_id,
                "parent_question": parent_question
            }
            event_publisher.publish_new_feedback(feedback_event)
            print(f"Feedback published: {feedback_event}, ")


        # Skip all other messages
        else:
            print(f"Skipping message with ID {ts} from user {user_id}. Reason: {skip_reason}")

        print(f"Current Questions: {self.questions}")
        print(f"Processed Messages: {self.processed_messages}")

    def is_valid_message(self, event):
        """ Check if the event is a valid user message """
        return event.get("type") == "message" and "subtype" not in event

    def determine_skip_reason(self, event, ts, text, thread_ts, user_id, bot_user_id):
        """ Determine the specific reason a message is being skipped """
        if user_id == bot_user_id:
            return "Message is from the bot itself"
        if not self.is_valid_message(event):
            return "Invalid message type or subtype"
        if thread_ts and thread_ts != ts:
            return "Message is a reply in a thread"
        if not "?" in text:
            return "Message does not contain a '?' and is not identified as a question"
        return "Unknown reason"


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
                consume_events()
                time.sleep(50)
        except KeyboardInterrupt:
            logging.info("Bot stopped by the user")
        except Exception as e:
            logging.critical("Bot stopped due to an exception", exc_info=True)


def load_slack_bot():
    logging.basicConfig(level=logging.DEBUG)
    event_handlers = [ChannelMessageHandler()]
    bot = SlackBot(slack_bot_user_oauth_token, slack_app_level_token, bot_user_id, event_handlers)
    bot.start()


def load_slack_bot_parallel():
    logging.basicConfig(level=logging.DEBUG)
    event_handlers = [ChannelMessageHandler()]
    bot = SlackBot(slack_bot_user_oauth_token, slack_app_level_token, bot_user_id, event_handlers)
    bot.start()


if __name__ == "__main__":
    load_slack_bot()
