# ./slack/event_consumer_assistants.py
from datetime import datetime
from slack.event_publisher import EventPublisher
from slack_sdk import WebClient
from credentials import slack_bot_user_oauth_token
from vector.chroma_threads import retrieve_relevant_documents
from database.nur_database import QAInteractionManager, Session, SlackMessageDeduplication
from threads.dynamic_executor_assistants import DynamicExecutor
from oai_assistants.query_assistant_from_documents import query_assistant_with_context
# from oai_assistants.query_assistant_rag_tool import query_assistant_with_context

class EventConsumer:
    """ Consumes events from the event queue and processes them."""
    def __init__(self, publisher: EventPublisher):
        """ Initializes the event consumer."""
        self.publisher = publisher
        self.web_client = WebClient(token=slack_bot_user_oauth_token)
        self.db_session = Session()
        self.interaction_manager = QAInteractionManager(self.db_session)
        self.executor = DynamicExecutor()
        print("\n\nSlack Event Consumer initiated successfully\n\n")

    def is_message_processed_in_db(self, channel_id, message_ts):
        """
        Checks if the message has already been processed and recorded in the database.
        """
        return self.db_session.query(SlackMessageDeduplication).filter_by(channel_id=channel_id,
                                                                          message_ts=message_ts).first() is not None

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

    def add_question_and_response_to_database(self, question_event, response_text, assistant_thread_id):
        """ Adds the question and response to the database."""
        self.interaction_manager.add_question_and_answer(
            question=question_event["text"],
            answer=response_text,
            thread_id=question_event["ts"],
            assistant_thread_id=assistant_thread_id,
            channel_id=question_event["channel"],
            question_ts=datetime.fromtimestamp(float(question_event["ts"])),
            answer_ts=datetime.now()
        )
        print(
            f"\n\nQuestion and answer stored in the database: question: {question_event},\nAnswer: {response_text},\nAssistant_id {assistant_thread_id}\n\n")

    def process_question(self, question_event):
        """
        Processes a single question event.
        retrieves relevant documents,
        queries the assistant with context,
        records the message as processed in the db,
        adds the question and response to the database,
        and posts the response to the Slack thread.
        """
        channel_id = question_event["channel"]
        message_ts = question_event["ts"]
        try:
            # Retrieve relevant document IDs
            context_page_ids = retrieve_relevant_documents(question_event["text"])
            response_text, assistant_thread_id = query_assistant_with_context(question_event["text"], context_page_ids,
                                                                          None)
        except Exception as e:
            print(f"Error processing question: {e}")
            response_text = None
        if response_text:
            print(f"Response from assistant: {response_text}\n")
            try:
                self.record_message_as_processed_in_db(channel_id, message_ts)
                self.add_question_and_response_to_database(question_event, response_text, assistant_thread_id)
                self.web_client.chat_postMessage(channel=channel_id, text=response_text, thread_ts=message_ts)
                print(f"\nResponse posted to Slack thread: {message_ts}\n")
            except Exception as e:
                print(f"Error registering message as processed, adding to db and responding to the question on slack: {e}")

    def generate_extended_context_query(self, existing_interaction, feedback_text):
        """ Generates an extended context query for feedback question by adding the existing interaction fields as one string with key value pairs."""
        extended_context_query = ""
        if existing_interaction:
            extended_context_query = f"Follow up: {feedback_text},"\
                                     f"Initial question: {existing_interaction.question_text}, " \
                                     f"Initial answer: {existing_interaction.answer_text} "
        # add conversation summary using gpt-3 or another context summarization library
        return extended_context_query

    def process_feedback(self, feedback_event):
        """ Processes a single feedback event."""
        channel_id = feedback_event["channel"]
        message_ts = feedback_event["ts"]
        thread_ts = feedback_event["thread_ts"]
        response_text = None

        try:
            # get existing interaction from db
            existing_interaction = self.interaction_manager.get_interaction_by_thread_id(thread_ts)
            assistant_thread_id = existing_interaction.assistant_thread_id if existing_interaction else None
            print(f"\n\nExisting interaction found: {existing_interaction}\n\n")
            print(f"\n\nAssistant thread ID: {assistant_thread_id}\n\n")
        except Exception as e:
            print(f"Error getting existing interaction from the database: {e}")
            existing_interaction = None
            assistant_thread_id = None
        if existing_interaction:
            # extended_context generated by adding existing interaction fields as one string with key value pairs
            extended_context_query = self.generate_extended_context_query(existing_interaction, feedback_event["text"])
            print(f"\n\nExtended context: {extended_context_query}\n\n")
            page_ids = retrieve_relevant_documents(extended_context_query)
            try:
                # query assistant with context
                response_text, assistant_thread_id = query_assistant_with_context(feedback_event["text"], page_ids,
                                                                                  assistant_thread_id)
            except Exception as e:
                print(f"Error processing feedback: {e}")
                response_text = None

        if response_text:
            print(f"Response from assistant: {response_text}\n")

            # record message as processed in the db
            self.record_message_as_processed_in_db(channel_id, message_ts)
            timestamp_str = datetime.now().isoformat()

            # add feedback to the interaction in the db
            comment = {"text": feedback_event["text"],
                       "user": feedback_event["user"],
                       "timestamp": timestamp_str,
                       "assistant reposnse": response_text}
            self.interaction_manager.add_comment_to_interaction(
                thread_id=thread_ts,
                comment=comment,
            )
            print(f"Feedback appended to the interaction in the database: {feedback_event}\n")

            # Post message to the Slack thread
            self.web_client.chat_postMessage(channel=channel_id, text=response_text, thread_ts=thread_ts)
            print(f"Feedback response posted to Slack thread: {message_ts}\n")
        else:
            print(f"No response generated for feedback: {feedback_event}\n")

    def consume_questions(self):
        """Consumes question events from the question queue."""
        # Process all the questions in the queue
        while not self.publisher.question_queue.empty():
            question_event = self.publisher.question_queue.get()
            # Check if the message has already been processed
            if not self.is_message_processed_in_db(question_event["channel"], question_event["ts"]):
                print(f"Processing new question event: {question_event}\n")
                # Process the question
                self.process_question(question_event)
            else:
                print(f"Skipping already processed message: {question_event}\n")
            # Mark the task as done
            self.publisher.question_queue.task_done()

    def consume_feedback(self):
        """Consumes feedback events from the feedback queue."""
        # Process all the feedback in the queue
        while not self.publisher.feedback_queue.empty():
            feedback_event = self.publisher.feedback_queue.get()
            channel_id = feedback_event["channel"]
            message_ts = feedback_event["ts"]

            # Check if the feedback has already been processed and process it or skip it
            if not self.is_message_processed_in_db(channel_id, message_ts):
                print(f"Processing new feedback event: {feedback_event}\n")
                self.process_feedback(feedback_event)
            else:
                print(f"Skipping already processed feedback: {feedback_event}\n")
            # Mark the task as done
            self.publisher.feedback_queue.task_done()


def consume_events():
    """Consumes events from the event queue."""
    publisher = EventPublisher()
    consumer = EventConsumer(publisher)
    consumer.consume_questions()
    consumer.consume_feedback()


if __name__ == "__main__":
    consume_events()
