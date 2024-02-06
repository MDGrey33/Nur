# ./slack/event_publisher.py
import os
import fcntl
from persistqueue import Queue
from configuration import persist_question_queue_path, persist_feedback_queue_path, persist_message_queue_path


class EventPublisher:
    def __init__(self):
        self.message_queue = Queue(os.path.join(persist_message_queue_path, "message_events"))
        self.question_queue = Queue(os.path.join(persist_question_queue_path, "question_events"))
        self.feedback_queue = Queue(os.path.join(persist_feedback_queue_path, "feedback_events"))
        # File paths for locking
        self.message_queue_lock_path = os.path.join(persist_message_queue_path, "message_events_lock")
        self.question_queue_lock_path = os.path.join(persist_question_queue_path, "question_events_lock")
        self.feedback_queue_lock_path = os.path.join(persist_feedback_queue_path, "feedback_events_lock")
        # Create lock files
        open(self.message_queue_lock_path, 'a').close()
        open(self.question_queue_lock_path, 'a').close()
        open(self.feedback_queue_lock_path, 'a').close()

    def publish_new_message(self, message_event):
        with open(self.message_queue_lock_path, 'r+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            self.message_queue.put(message_event)
            fcntl.flock(f, fcntl.LOCK_UN)
        print(f"New message event enqueued: {message_event}")

    def publish_new_question(self, question_event):
        with open(self.question_queue_lock_path, 'r+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            self.question_queue.put(question_event)
            fcntl.flock(f, fcntl.LOCK_UN)
        print(f"New question event enqueued: {question_event}")

    def publish_new_feedback(self, feedback_event):
        with open(self.feedback_queue_lock_path, 'r+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            self.feedback_queue.put(feedback_event)
            fcntl.flock(f, fcntl.LOCK_UN)
        print(f"New feedback event enqueued: {feedback_event}")
