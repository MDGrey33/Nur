from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from credentials import slack_bot_user_oauth_token, slack_app_level_token


class SlackClient:
    def __init__(self):
        self.web_client = WebClient(token=slack_bot_user_oauth_token)
        self.socket_mode_client = SocketModeClient(
            app_token=slack_app_level_token, web_client=self.web_client
        )
