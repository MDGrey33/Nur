import pulsar
import time


class PulsarClient:
    def __init__(self, service_url):
        self.client = pulsar.Client(service_url)

    def publish_message(self, topic, message):
        producer = self.client.create_producer(topic)
        producer.send(message.encode('utf-8'))
        print(f"Message published to topic '{topic}': {message}")
        producer.close()

    def consume_message(self, topic, subscription_name):
        consumer = self.client.subscribe(topic, subscription_name)
        msg = None  # Initialize msg before the try block

        try:
            msg = consumer.receive(timeout_millis=5000)  # waits for 5 seconds for a message
            if msg:
                print("Received message: '{}'".format(msg.data().decode('utf-8')))
                consumer.acknowledge(msg)
                return msg.data().decode('utf-8')  # Return the message content
            else:
                print("No message received within the timeout period.")
                return None
        except Exception as e:
            print("Failed to process message: ", e)
            if msg:  # Check if msg is not None
                consumer.negative_acknowledge(msg)
            return None
        finally:
            consumer.close()

    def close(self):
        self.client.close()


if __name__ == "__main__":
    client = PulsarClient("pulsar://localhost:6650")
    topic = "my-topic"
    subscription_name = "my-subscription"

    # Publishing a message
    client.publish_message(topic, "Hello, Pulsar!")

    # Waiting for a short period
    print("Waiting for 10 seconds before consuming the message...")
    time.sleep(10)

    # Consuming the message
    client.consume_message(topic, subscription_name)

    # Closing the Pulsar client
    client.close()
