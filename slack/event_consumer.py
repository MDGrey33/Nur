from event_publisher import EventPublisher
from slack_sdk import WebClient
from credentials import slack_bot_user_oauth_token
from vector.chroma import retrieve_relevant_documents
from gpt_4t.query_from_documents import query_gpt_4t_with_context


class EventConsumer:
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher
        self.web_client = WebClient(token=slack_bot_user_oauth_token)

    def process_message_event(self, event_data):
        print("Processing new event:", event_data)  # Detailed diagnostic output

        # Validate required keys directly from the event_data
        if "channel" in event_data and "text" in event_data and "ts" in event_data:
            channel_id = event_data["channel"]
            text = event_data["text"]
            thread_ts = event_data["ts"]

            print(f"Event details - User: {event_data.get('user')}, Channel: {channel_id}, Text: {text}")

            if "?" in text:  # Check if the message is a question
                print("Identified message as a question.")
                response_text = self.generate_response(text)
            else:
                print("Identified message as not a question.")
                response_text = f"Received your message: '{text}'"

            # Post response back to Slack if all required information is present
            if channel_id and thread_ts and response_text:
                print(f"Posting response to channel {channel_id}")
                self.web_client.chat_postMessage(channel=channel_id, text=response_text, thread_ts=thread_ts)
            else:
                print("Missing information required for posting response:",
                      {"channel_id": channel_id, "thread_ts": thread_ts, "response_text": response_text})
        else:
            print("Event does not contain expected keys:", event_data)

    def generate_response(self, question):
        # Placeholder logic for generating a response
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
            # Placeholder for reaction event processing
            print("Processing reaction event:", reaction_event)
            self.publisher.reaction_queue.task_done()

if __name__ == "__main__":
    publisher = EventPublisher()
    consumer = EventConsumer(publisher)
    consumer.consume_messages()
    consumer.consume_reactions()
