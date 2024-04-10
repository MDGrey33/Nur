# /nurai/chat_services/slack/slack_service.py
from ..chat_service_interface import ChatServiceInterface
from .slack_client import SlackClient
from .event_handlers.event_handler_factory import SlackEventHandlerFactory
from nurai.logger.logger import setup_logger

logging = setup_logger()


class SlackService(ChatServiceInterface):
    def start_service(self):
        slack_client = SlackClient()
        bot_user_id = slack_client.get_bot_user_id()
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
