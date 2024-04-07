from app.chat_services.chat_service_interface import ChatServiceInterface
from .slack_client import SlackClient
from app.chat_services.slack.event_handlers.event_handler_factory import (
    SlackEventHandlerFactory,
)
from slack.client import get_bot_user_id
import logging


class SlackService(ChatServiceInterface):
    def start_service(self):
        bot_user_id = get_bot_user_id()
        slack_client = SlackClient()
        # Initialize the EventHandlerFactory
        event_handler_factory = SlackEventHandlerFactory()

        def handle_event(_, req):
            # Use the factory to get the appropriate handler based on the event
            handler = event_handler_factory.get_handler(req.payload, bot_user_id)
            handler.handle(
                client=slack_client.socket_mode_client,
                req=req,
                web_client=slack_client.web_client,
                bot_user_id=bot_user_id,
            )

        slack_client.socket_mode_client.socket_mode_request_listeners.append(
            handle_event
        )

        slack_client.socket_mode_client.connect()
        logging.info("Slack Bot has started successfully.")
