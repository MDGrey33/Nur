from nurai.chat_services.slack.event_handlers.event_handler import SlackEventHandler
from nurai.chat_services.slack.event_handlers.event_handlers import (
    SimpleMessageHandler,
    ReplyMessageHandler,
    ReactionAddedHandler,
    BotDirectMessageHandler,
    BotMentionHandler,
)
from nurai.logger.logger import setup_logger

# The package name is automatically deduced
logging = setup_logger()


class SlackEventHandlerFactory:
    @staticmethod
    def get_handler(payload, bot_user_id):
        event_type = payload.get("event", {}).get("type")
        thread_ts = payload.get("event", {}).get("thread_ts")
        channel_type = payload.get("event", {}).get("channel_type")
        text = payload.get("event", {}).get("text", "")

        if event_type == "message" and not thread_ts and channel_type != "im":
            return SimpleMessageHandler()
        elif event_type == "message" and thread_ts:
            return ReplyMessageHandler()
        elif event_type == "reaction_added":
            return ReactionAddedHandler()
        elif event_type == "message" and channel_type == "im":
            return BotDirectMessageHandler()
        elif "<@" + bot_user_id + ">" in text:
            return BotMentionHandler()
        else:
            return DefaultHandler()  # Handle unknown message types


class DefaultHandler(SlackEventHandler):
    def handle(self, client, req, web_client, bot_user_id):
        logging.info("Handling unknown message type")
