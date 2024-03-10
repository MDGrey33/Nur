import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def get_bot_user_id(bot_oauth_token):
    """Get the bot user id from the slack api"""
    slack_client = WebClient(token=bot_oauth_token)
    try:
        response = slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        logging.error(f"Error fetching bot user ID: {e.response['error']}")
        return "unassigned"
