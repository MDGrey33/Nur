# /nurai/chat_services/slack/slack_service.py
from ..chat_service_interface import ChatServiceInterface
from .slack_client import SlackClient
from .event_handlers.event_handler_factory import SlackEventHandlerFactory
from nurai.logger.logger import setup_logger


logging = setup_logger()


class SlackService(ChatServiceInterface):

    def __init__(self):
        self.slack_client = SlackClient()

    def start_service(self):
        bot_user_id = self.slack_client.get_bot_user_id()
        event_handler_factory = SlackEventHandlerFactory()

        def handle_event(_, req):
            handler = event_handler_factory.get_handler(req.payload, bot_user_id)
            handler.handle(
                client=self.slack_client.socket_mode_client,
                req=req, web_client=self.slack_client.web_client,
                bot_user_id=bot_user_id
            )

        self.slack_client.socket_mode_client.socket_mode_request_listeners.append(
            handle_event
        )
        self.slack_client.socket_mode_client.connect()
        logging.info("Slack service has started successfully.")

    def fetch_thread_messages(self, channel, thread_ts):
        return self.slack_client.fetch_thread_messages(channel, thread_ts)

    def transform_messages_to_interaction_input(self, messages, channel_id):
        return self.slack_client.transform_messages_to_interaction_input(messages, channel_id)
