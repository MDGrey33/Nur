# ./slack/event_publisher.py
import os
from persistqueue import Queue
from configuration import persist_message_queue_path, persist_reaction_queue_path


class EventPublisher:
    def __init__(self):
        self.message_queue = Queue(os.path.join(persist_message_queue_path, "message_events"))
        self.reaction_queue = Queue(os.path.join(persist_reaction_queue_path, "reaction_events"))

    def publish_new_message(self, message_event):
        self.message_queue.put(message_event)
        print(f"New message event enqueued: {message_event}")

    def publish_new_reaction(self, reaction_event):
        self.reaction_queue.put(reaction_event)
        print(f"New reaction event enqueued: {reaction_event}")