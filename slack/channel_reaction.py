import logging
import time
from abc import ABC, abstractmethod
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from credentials import slack_bot_user_oauth_token, slack_app_level_token


class SlackEventHandler(ABC):
    @abstractmethod
    def handle(self, client: SocketModeClient, req: SocketModeRequest, web_client: WebClient, bot_user_id: str):
        pass


class ChannelMessageHandler(SlackEventHandler):
    def handle(self, client: SocketModeClient, req: SocketModeRequest, web_client: WebClient, bot_user_id: str):
        try:
            logging.debug(f"Received event: {req.payload}")
            if req.type == "events_api":
                event = req.payload.get("event", {})
                logging.info(f"Event details: {event}")

                if event.get("type") == "message" and "subtype" not in event and event.get("user") != bot_user_id:
                    text = event.get("text", "")
                    channel_id = event["channel"]
                    logging.info(f"Message received: '{text}' in channel {channel_id}")

                    response_message = f"I got a message from you saying \"{text}\""
                    web_client.chat_postMessage(channel=channel_id, text=response_message)
                    logging.info(f"Sent response in channel {channel_id}")

                client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
        except Exception as e:
            logging.error(f"Error processing event: {e}", exc_info=True)


class SlackBot:
    def __init__(self, token: str, app_token: str, bot_user_id: str, event_handler: SlackEventHandler):
        self.web_client = WebClient(token=token)
        self.socket_mode_client = SocketModeClient(app_token=app_token, web_client=self.web_client)
        self.bot_user_id = bot_user_id
        self.event_handler = event_handler

    def start(self):
        from functools import partial
        event_handler = partial(self.event_handler.handle, web_client=self.web_client, bot_user_id=self.bot_user_id)
        self.socket_mode_client.socket_mode_request_listeners.append(event_handler)
        self.socket_mode_client.connect()

        try:
            while True:
                logging.debug("Bot is running...")
                time.sleep(10)
        except KeyboardInterrupt:
            logging.info("Bot stopped by the user")
        except Exception as e:
            logging.critical("Bot stopped due to an exception", exc_info=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot_user_id = "U069C17DCE5"  # Replace with your bot's actual user ID
    event_handler = ChannelMessageHandler()
    bot = SlackBot(slack_bot_user_oauth_token, slack_app_level_token, bot_user_id, event_handler)
    bot.start()
