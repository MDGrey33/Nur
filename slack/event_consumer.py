# ./slack/event_consumer.py
from event_publisher import EventPublisher


class EventConsumer:
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher

    def consume_messages(self):
        while not self.publisher.message_queue.empty():
            message_event = self.publisher.message_queue.get()
            print(f"Consuming message event: {message_event}")
            self.publisher.message_queue.task_done()

    def consume_reactions(self):
        while not self.publisher.reaction_queue.empty():
            reaction_event = self.publisher.reaction_queue.get()
            print(f"Consuming reaction event: {reaction_event}")
            self.publisher.reaction_queue.task_done()


if __name__ == "__main__":
    publisher = EventPublisher()
    consumer = EventConsumer(publisher)
    consumer.consume_messages()
    consumer.consume_reactions()
