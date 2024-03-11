import logging
from slack_sdk.socket_mode.response import SocketModeResponse
from database.interaction_manager import QAInteractionManager
from slack.event_handler import SlackEventHandler
from slack_sdk import WebClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode import SocketModeClient
from configuration import api_host, api_port
import requests
import os
from slack.reaction_manager import process_checkmark_added_event


host = os.environ.get("NUR_API_HOST", api_host)
port = os.environ.get("NUR_API_PORT", api_port)



class ChannelMessageHandler(SlackEventHandler):
    """Handles incoming messages from the channel and publishes questions and feedback to the persist queue"""

    def __init__(self):
        self.interaction_manager = QAInteractionManager()
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

        # Assuming 'event' is the dictionary representing the Slack event received,
        # and 'web_client' is an instance of slack_sdk.WebClient initialized with your bot token.
        if event.get("type") == "reaction_added":
            # check if the reaction': is 'white_check_mark'
            if event.get("reaction") == "white_check_mark":
                process_checkmark_added_event(slack_web_client=web_client, event=event)
        # identify if the bot is trying to gather knowledge
        if user_id == bot_user_id and not thread_ts and "?" in text and "Question:" in text:
            # print the message text to the console
            print(text)
            print(f"Bot gathering knowledge\ntext:{text}\n")
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
                response = requests.post(f'http://{host}:{port}/api/v1/questions/', json=question_event)
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
                response = requests.post(f'http://{host}:{port}/api/v1/feedback/', json=feedback_event)
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
