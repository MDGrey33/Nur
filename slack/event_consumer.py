# ./slack/event_consumer.py
import json
from datetime import datetime
from slack.event_publisher import EventPublisher
from slack_sdk import WebClient
from credentials import slack_bot_user_oauth_token
from vector.chroma import retrieve_relevant_documents
from gpt_4t.query_from_documents import query_gpt_4t_with_context
from database.confluence_database import QAInteractionManager, session

class EventConsumer:
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher
        self.web_client = WebClient(token=slack_bot_user_oauth_token)
        self.processed_ids_file = 'processed_ids.json'
        self.load_processed_message_ids()
        self.bot_user_id = self.web_client.auth_test().get('user_id')  # Get the bot user ID

    def load_processed_message_ids(self):
        try:
            with open(self.processed_ids_file, 'r') as file:
                self.processed_message_ids = set(json.load(file))
        except (FileNotFoundError, json.JSONDecodeError):
            self.processed_message_ids = set()

    def save_processed_message_ids(self):
        with open(self.processed_ids_file, 'w') as file:
            json.dump(list(self.processed_message_ids), file)

    def process_message_event(self, event_data):
        print("Processing new event:", event_data)  # Detailed diagnostic output

        message_id = event_data.get("client_msg_id")
        user_id = event_data.get("user")

        # Skip if the message is from the bot itself or already processed
        if user_id == self.bot_user_id or message_id in self.processed_message_ids:
            print(f"Skipping message: {message_id}")
            return

        # Validate required keys directly from the event_data
        if "channel" in event_data and "text" in event_data and "ts" in event_data:
            channel_id = event_data["channel"]
            text = event_data["text"]
            thread_ts = event_data["ts"]

            # Determine the type of message and generate an appropriate response
            if "?" in text:  # Check if the message is a question
                response_text = self.generate_response(text)
                # Update the database with the question and answer
                qa_manager = QAInteractionManager(session)
                qa_manager.add_question_and_answer(
                    question=text,
                    answer=response_text,
                    thread_id=thread_ts,  # This becomes the identifier for the interaction
                    channel_id=channel_id,
                    question_ts=datetime.fromtimestamp(float(thread_ts)),
                    answer_ts=datetime.now()
                )
            else:
                response_text = f"Received your message: '{text}'"

            # Post response back to Slack if all required information is present
            if channel_id and thread_ts and response_text:
                self.web_client.chat_postMessage(channel=channel_id, text=response_text, thread_ts=thread_ts)

            # Mark this message as processed
            self.processed_message_ids.add(message_id)
            self.save_processed_message_ids()
        else:
            print("Event does not contain expected keys:", event_data)

    def generate_response(self, question):
        file_name = "context.txt"  # Placeholder for actual context retrieval logic
        relevant_document_ids = retrieve_relevant_documents(question)
        response_text = query_gpt_4t_with_context(question, relevant_document_ids)
        return response_text

    def consume_messages(self):
        while not self.publisher.message_queue.empty():
            message_event = self.publisher.message_queue.get()
            self.process_message_event(message_event)
            self.publisher.message_queue.task_done()

    def consume_reactions(self):
        while not self.publisher.reaction_queue.empty():
            reaction_event = self.publisher.reaction_queue.get()
            print("Processing reaction event:", reaction_event)
            self.publisher.reaction_queue.task_done()

def consume_events():
    publisher = EventPublisher()
    consumer = EventConsumer(publisher)
    consumer.consume_messages()
    consumer.consume_reactions()

if __name__ == "__main__":
    consume_events()
