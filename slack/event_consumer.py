from datetime import datetime
from slack.event_publisher import EventPublisher
from slack_sdk import WebClient
from credentials import slack_bot_user_oauth_token
from vector.chroma import retrieve_relevant_documents
from gpt_4t.query_from_documents import query_gpt_4t_with_context
from database.confluence_database import QAInteractionManager, Session


class EventConsumer:
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher
        self.web_client = WebClient(token=slack_bot_user_oauth_token)
        self.db_session = Session()
        self.interaction_manager = QAInteractionManager(self.db_session)

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

    def consume_questions(self):
        while not self.publisher.question_queue.empty():
            question_event = self.publisher.question_queue.get()
            self.publisher.question_queue.task_done()

            print("Processing question event:", question_event)

            # Generate response and store the interaction
            response_text = self.generate_response(question_event["text"])
            print(f"Response generated: {response_text}")

            # Add the question and response to the database
            self.add_question_and_response_to_database(question_event, response_text)

            # Post the response in the same thread as the question
            self.web_client.chat_postMessage(
                channel=question_event["channel"],
                text=response_text,
                thread_ts=question_event["ts"]  # This ensures the message is part of the same thread
            )
            print(f"Response posted to Slack thread: {question_event['ts']}")

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
