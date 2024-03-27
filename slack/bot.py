import logging
from functools import partial
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from credentials import slack_bot_user_oauth_token, slack_app_level_token
from slack.channel_message_handler import ChannelMessageHandler
from slack.client import get_bot_user_id
import time


class SlackBot:
    def __init__(self, token, app_token, bot_user_id, event_handlers):
        self.web_client = WebClient(token=token)
        self.socket_mode_client = SocketModeClient(
            app_token=app_token, web_client=self.web_client
        )
        self.bot_user_id = bot_user_id
        self.event_handlers = event_handlers

    def start(self):
        """Start the bot and listen to events"""
        # Add event handlers to the socket mode client
        for event_handler in self.event_handlers:
            event_handler_func = partial(
                event_handler.handle,
                web_client=self.web_client,
                bot_user_id=self.bot_user_id,
            )
            self.socket_mode_client.socket_mode_request_listeners.append(
                event_handler_func
            )

        # Connect to the slack RTM API
        try:
            self.socket_mode_client.connect()
        except Exception as e:
            logging.error(f"Error connecting to the slack RTM API: {e}")

        try:
            while True:
                logging.debug("Bot is running...")
                time.sleep(1000)
        # Stop the bot if the user interrupts
        except KeyboardInterrupt:
            logging.info("Bot stopped by the user")
        # Stop the bot if an exception occurs
        except Exception as e:
            logging.critical("Bot stopped due to an exception", exc_info=True)


def load_slack_bot():
    logging.basicConfig(level=logging.INFO)
    bot_user_id = get_bot_user_id(slack_bot_user_oauth_token)
    event_handlers = [ChannelMessageHandler()]
    bot = SlackBot(
        slack_bot_user_oauth_token, slack_app_level_token, bot_user_id, event_handlers
    )
    bot.start()


if __name__ == "__main__":
    load_slack_bot()
