# ./slack/event_publisher.py
import os
from persistqueue import Queue
from configuration import persist_question_queue_path, persist_feedback_queue_path


class EventPublisher:
    def __init__(self):
        self.question_queue = Queue(os.path.join(persist_question_queue_path, "question_events"))
        self.feedback_queue = Queue(os.path.join(persist_feedback_queue_path, "feedback_events"))

    def publish_new_question(self, question_event):
        self.question_queue.put(question_event)
        print(f"New question event enqueued: {question_event}")

    def publish_new_feedback(self, feedback_event):
        self.feedback_queue.put(feedback_event)
        print(f"New feedback event enqueued: {feedback_event}")