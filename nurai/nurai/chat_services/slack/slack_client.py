from slack_sdk.socket_mode import SocketModeClient
from credentials import slack_bot_user_oauth_token, slack_app_level_token
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackClient:
    def __init__(self):
        self.web_client = WebClient(token=slack_bot_user_oauth_token)
        self.socket_mode_client = SocketModeClient(
            app_token=slack_app_level_token, web_client=self.web_client
        )
        # Store the bot_user_id as an instance variable
        self.bot_user_id = self.get_bot_user_id()

    def get_bot_user_id(self, bot_oauth_token=slack_bot_user_oauth_token):
        """Get the bot user id from the slack api"""
        try:
            response = self.web_client.auth_test()
            return response["user_id"]
        except SlackApiError as e:
            logging.error(f"Error fetching bot user ID: {e.response['error']}")
            return "unassigned"
