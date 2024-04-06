from app.chat_services.chat_service_interface import ChatServiceInterface
from .slack_client import SlackClient
from .channel_message_handler import ChannelMessageHandler
from slack.client import get_bot_user_id
import logging


class SlackService(ChatServiceInterface):
    def start_service(self):
        bot_user_id = get_bot_user_id()
        slack_client = SlackClient()
        event_handlers = [ChannelMessageHandler()]

        for handler in event_handlers:
            slack_client.socket_mode_client.socket_mode_request_listeners.append(
                lambda _, req: handler.handle(
                    client=slack_client.socket_mode_client,
                    req=req,
                    web_client=slack_client.web_client,
                    bot_user_id=bot_user_id,
                )
            )
        slack_client.socket_mode_client.connect()
        logging.info("Slack Bot has started successfully.")
