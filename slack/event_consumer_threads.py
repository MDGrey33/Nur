# ./slack/event_consumer_threads.py
from datetime import datetime
from slack.event_publisher import EventPublisher
from slack_sdk import WebClient
from credentials import slack_bot_user_oauth_token
from vector.chroma_threads import retrieve_relevant_documents
from gpt_4t.query_from_documents_threads import query_gpt_4t_with_context
from database.nur_database import QAInteractionManager, Session, SlackMessageDeduplication
from threads.dynamic_executor import DynamicExecutor
from gpt_4t.query_from_documents_threads import format_pages_as_context

print("imports completed successfully")


class EventConsumer:
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher
        self.web_client = WebClient(token=slack_bot_user_oauth_token)
        self.db_session = Session()
        self.interaction_manager = QAInteractionManager(self.db_session)
        self.executor = DynamicExecutor()
        print("dynamic executor initiated successfully")

    def is_message_processed_in_db(self, channel_id, message_ts):
        """
        Checks if the message has already been processed and recorded in the database.
        """
        return self.db_session.query(SlackMessageDeduplication).filter_by(channel_id=channel_id, message_ts=message_ts).first() is not None

    def record_message_as_processed_in_db(self, channel_id, message_ts):
        """
        Records the message as processed in the database by adding its channel ID and timestamp to the SlackMessageDeduplication table.
        """
        dedup_record = SlackMessageDeduplication(
            channel_id=channel_id,
            message_ts=message_ts
        )
        self.db_session.add(dedup_record)
        self.db_session.commit()

    def generate_response(self, question):
        relevant_document_ids = retrieve_relevant_documents(question)
        response_text = query_gpt_4t_with_context(question, relevant_document_ids)
        return response_text

    def add_question_and_response_to_database(self, question_event, response_text):
        self.interaction_manager.add_question_and_answer(
            question=question_event["text"],
            answer=response_text,
            thread_id=question_event["ts"],
            channel_id=question_event["channel"],
            question_ts=datetime.fromtimestamp(float(question_event["ts"])),
            answer_ts=datetime.now()
        )
        print(f"Question and answer stored in the database: {question_event}")

    def process_question(self, question_event):
        """
        Processes a single question event.
        """
        channel_id = question_event["channel"]
        message_ts = question_event["ts"]

        # Retrieve relevant document IDs (context) synchronously as it's fast
        relevant_document_ids = retrieve_relevant_documents(question_event["text"])
        context = format_pages_as_context(relevant_document_ids)


        # Generate the response using the dynamic executor
        self.executor.add_task(question_event["text"], context)

        # Retrieve and process the response as soon as it's available
        response_text = self.executor.get_next_result()

        if response_text:
            # Record the message as processed in the database
            self.record_message_as_processed_in_db(channel_id, message_ts)
            self.add_question_and_response_to_database(question_event, response_text)

            # Post the response back to the Slack channel
            self.web_client.chat_postMessage(
                channel=channel_id,
                text=response_text,
                thread_ts=message_ts
            )
            print(f"Response posted to Slack thread: {message_ts}")

    def consume_questions(self):
        while not self.publisher.question_queue.empty():
            question_event = self.publisher.question_queue.get()

            if not self.is_message_processed_in_db(question_event["channel"], question_event["ts"]):
                print(f"Processing new question event: {question_event}")
                self.process_question(question_event)
            else:
                print(f"Skipping already processed message: {question_event}")

            self.publisher.question_queue.task_done()

    def consume_feedback(self):
        while not self.publisher.feedback_queue.empty():
            feedback_event = self.publisher.feedback_queue.get()
            print("Processing feedback event:", feedback_event)

            # Append the feedback to the corresponding interaction
            timestamp_str = datetime.now().isoformat()
            self.interaction_manager.add_comment_to_interaction(
                thread_id=feedback_event["thread_ts"],
                comment={
                    "text": feedback_event["text"],
                    "user": feedback_event["user"],
                    "timestamp": timestamp_str
                }
            )
            print(f"Feedback appended to the interaction in the database: {feedback_event}")
            self.publisher.feedback_queue.task_done()


def consume_events():
    publisher = EventPublisher()
    consumer = EventConsumer(publisher)
    consumer.consume_questions()
    consumer.consume_feedback()


if __name__ == "__main__":
    consume_events()
