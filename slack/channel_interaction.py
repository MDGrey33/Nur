# ./slack/channel_interaction_assistants.py
import logging
import time
import requests
from functools import partial
from abc import ABC, abstractmethod
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from typing import List
from credentials import slack_bot_user_oauth_token, slack_app_level_token
from slack.event_publisher import EventPublisher
from slack.event_consumer_assistants import consume_events
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from database.nur_database_assistants import Session, QAInteractionManager


# get slack bot user id
def get_bot_user_id(bot_oauth_token):
    """Get the bot user id from the slack api"""
    # Initialize WebClient with your bot's token
    slack_client = WebClient(token=bot_oauth_token)
    bot_id = "unassigned"
    try:
        # Call the auth.test method using the Slack client
        response = slack_client.auth_test()
        bot_id = response["user_id"]
        logging.info(f"\n\nBot User ID: {bot_id}\n\n")
    except SlackApiError as e:
        logging.info(f"\n\nError fetching bot user ID: {e.response['error']}\n\n")
    return bot_id


class SlackEventHandler(ABC):
    @abstractmethod
    def handle(self, client: SocketModeClient, req: SocketModeRequest, web_client: WebClient, bot_user_id: str):
        pass


class ChannelMessageHandler(SlackEventHandler):
    """Handles incoming messages from the channel and publishes questions and feedback to the persist queue"""

    def __init__(self):
        self.db_session = Session()
        self.interaction_manager = QAInteractionManager(self.db_session)
        self.processed_messages = set()
        self.questions = {}
        self.load_processed_data()

    def load_processed_data(self):
        """ Load processed messages and questions from the database """
        try:
            interactions = self.interaction_manager.get_all_interactions()
        except Exception as e:
            logging.error(f"Error loading processed messages and questions: {e}")
            interactions = []
        for interaction in interactions:
            # Add to processed messages
            try:
                self.processed_messages.add(interaction.thread_id)
            except Exception as e:
                logging.error(f"Error adding processed message to interaction: {e}")
            # If it's a question, add to questions
            if interaction.question_text:
                try:
                    self.questions[interaction.thread_id] = interaction.question_text
                except Exception as e:
                    logging.error(f"Error adding question to interaction: {e}")

    def handle(self, client: SocketModeClient, req: SocketModeRequest, web_client: WebClient, bot_user_id: str):
        """Handle incoming messages from the channel and publish questions and feedback to the persist queue"""
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
            logging.info(f"Message {ts} already processed. Skipping.\n")
            return

        # Determine the reason for skipping before the checks
        skip_reason = self.determine_skip_reason(event, ts, text, thread_ts, user_id, bot_user_id)

        # Skip if message is invalid or from the bot itself
        if not self.is_valid_message(event) or user_id == bot_user_id:
            logging.warning(
                f"Skipping message with ID {ts} and Parent id {thread_ts} from user {user_id}. Reason: {skip_reason}")
            logging.info(f"Skipping message with ID {ts} from user {user_id}. Reason: {skip_reason}")
            return

        # Identify and handle questions
        if "?" in text and (not thread_ts):  # It's a question if not part of another thread
            logging.debug(f"Question identified: {text}")
            self.questions[ts] = text
            question_event = {
                "text": text,  # Message content
                "ts": ts,  # Message timestamp acting as unique ID in slack
                "thread_ts": "",  # Knowing it's a question on the main channel, we can set this to empty string
                "channel": channel,
                "user": user_id
            }
            # publish question event to the persist queue
            try:
                # Make an API call to publish the question
                response = requests.post("http://localhost:8000/api/v1/questions/", json=question_event)
                response.raise_for_status()
                logging.info(f"Question event published: {question_event}")

            except Exception as e:
                logging.error(f"Error publishing question event: {e}")

        # Identify and handle feedback
        elif thread_ts in self.questions:  # Message is a reply to a question
            parent_question = self.questions[thread_ts]
            logging.debug(f"Feedback identified for question '{parent_question}': {text}")
            feedback_event = {
                "text": text,  # Message content
                "ts": ts,  # Message timestamp acting as unique ID in slack
                "thread_ts": thread_ts,  # Parent message timestamp used to link feedback to question
                "channel": channel,
                "user": user_id,
                "parent_question": parent_question
            }
            # publish feedback event to the persist queue
            try:
                # Make an API call to publish the feedback
                response = requests.post("http://localhost:8000/api/v1/feedback/", json=feedback_event)
                response.raise_for_status()
                logging.info(f"Feedback published: {feedback_event}")
            except Exception as e:
                logging.error(f"Error publishing feedback event: {e}")

        # Skip all other messages
        else:
            logging.info(f"Skipping message with ID {ts} from user {user_id}. Reason: {skip_reason}")

        # Update the processed_messages set with the 'ts'
        try:
            self.processed_messages.add(ts)
        except Exception as e:
            logging.error(f"Error adding message to processed messages: {e}")

        logging.debug(f"Current Questions: {self.questions}")
        logging.debug(f"Processed Messages: {self.processed_messages}")

    def is_valid_message(self, event):
        """ Check if the event is a valid user message """
        return "subtype" not in event and (event.get("type") == "message" or event.get("type") == "app_mention")

    def determine_skip_reason(self, event, ts, text, thread_ts, user_id, bot_user_id):
        """ Determine the specific reason a message is being skipped """
        if user_id == bot_user_id:
            return "Message is from the bot itself"
        if not self.is_valid_message(event):
            return "Invalid message type or subtype" # Usually a modification or deletion
        if thread_ts and thread_ts != ts:
            return "Message is a reply in a thread that is not a question"
        if not "?" in text:
            return "Message on main channel and does not contain a '?' it is not identified as a question"
        return "Unknown reason"


class SlackBot:
    """A bot that listens to events from slack and processes them using event handlers"""
    def __init__(self, token: str, app_token: str, bot_user_id: str, event_handlers: List[SlackEventHandler]):
        """ Initialize the bot with the necessary tokens and event handlers"""
        self.web_client = WebClient(token=token)
        self.socket_mode_client = SocketModeClient(app_token=app_token, web_client=self.web_client)
        self.bot_user_id = bot_user_id
        self.event_handlers = event_handlers

    def start(self):
        """Start the bot and listen to events"""
        # Add event handlers to the socket mode client
        for event_handler in self.event_handlers:
            event_handler_func = partial(event_handler.handle, web_client=self.web_client, bot_user_id=self.bot_user_id)
            self.socket_mode_client.socket_mode_request_listeners.append(event_handler_func)

        # Connect to the slack RTM API
        try:
            self.socket_mode_client.connect()
        except Exception as e:
            logging.error(f"Error connecting to the slack RTM API: {e}")

        try:
            while True:
                logging.debug("Bot is running...")
                # Consume events from the persist queue
                consume_events()
                # Sleep for 10 seconds should be moved to 50 if we are facing errors
                time.sleep(10)
        # Stop the bot if the user interrupts
        except KeyboardInterrupt:
            logging.info("Bot stopped by the user")
        # Stop the bot if an exception occurs
        except Exception as e:
            logging.critical("Bot stopped due to an exception", exc_info=True)


def load_slack_bot():
    """Load the slack bot"""
    logging.basicConfig(level=logging.INFO)
    # Initialize the bot with the necessary tokens and event handlers
    event_handlers = [ChannelMessageHandler()]
    bot = SlackBot(slack_bot_user_oauth_token, slack_app_level_token, bot_user_id, event_handlers)
    bot.start()


bot_user_id = get_bot_user_id(slack_bot_user_oauth_token)

# Initialize EventPublisher instance
event_publisher = EventPublisher()

if __name__ == "__main__":
    try:
        load_slack_bot()
    except Exception as e:
        logging.critical("Error loading slack bot", exc_info=True)
