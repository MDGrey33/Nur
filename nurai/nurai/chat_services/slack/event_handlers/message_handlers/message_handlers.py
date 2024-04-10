# /nurai/chat_services/slack/event_handlers/event_handlers.py
from nurai.chat_services.slack.event_handlers.event_handler import SlackEventHandler
from nurai.logger.logger import setup_logger


# The package name is automatically deduced
logging = setup_logger()


class SimpleMessageHandler(SlackEventHandler):
    def handle(self, client, req, web_client, bot_user_id):
        logging.info("Handling simple message on a channel")


class ReplyMessageHandler(SlackEventHandler):
    def handle(self, client, req, web_client, bot_user_id):
        logging.info("Handling reply to a message in a thread")


class BotDirectMessageHandler(SlackEventHandler):
    def handle(self, client, req, web_client, bot_user_id):
        logging.info("Handling bot direct message")


class BotMentionHandler(SlackEventHandler):
    def handle(self, client, req, web_client, bot_user_id):
        logging.info("Handling bot mention in the channel or thread")
