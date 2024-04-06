from app.chat_services.slack.event_handler import SlackEventHandler
from app.logging.logger import setup_logger

# The package name is automatically deduced
logging = setup_logger()


class ChannelMessageHandler(SlackEventHandler):
    def handle(self, client, req, web_client, bot_user_id):
        # Implementation for handling channel messages
        logging.info("Handling channel messages")
