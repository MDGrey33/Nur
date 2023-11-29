import logging
from pulsar import Client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_message(service_url, topic, message_content):
    logger.info("Creating Pulsar client.")
    client = Client(service_url)

    logger.info(f"Creating producer for topic: {topic}.")
    producer = client.create_producer(topic)

    logger.info(f"Sending message: {message_content}.")
    producer.send(message_content.encode('utf-8'))

    logger.info("Message sent. Closing producer.")
    producer.close()

    logger.info("Producer closed. Closing client.")
    client.close()


def receive_messages(service_url, topic, subscription_name, num_messages):
    logger.info("Creating Pulsar client.")
    client = Client(service_url)

    logger.info(f"Subscribing to topic: {topic} with subscription name: {subscription_name}.")
    consumer = client.subscribe(topic, subscription_name)

    received_messages = []
    for _ in range(num_messages):
        logger.info("Waiting to receive a message.")
        msg = consumer.receive()
        message_data = msg.data().decode('utf-8')
        received_messages.append(message_data)
        logger.info(f"Received message: {message_data}")
        consumer.acknowledge(msg)

    logger.info("Messages received. Closing consumer.")
    consumer.close()

    logger.info("Consumer closed. Closing client.")
    client.close()

    return received_messages


# Test sending and receiving a message
service_url = 'pulsar://localhost:6650'
topic = 'test-topic'
message_content = 'Hello, Pulsar!'

logger.info("Starting test: sending a message.")
send_message(service_url, topic, message_content)