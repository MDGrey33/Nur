from slack_sdk.socket_mode import SocketModeClient
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from nurai.logger.logger import setup_logger

logging = setup_logger()


slack_bot_user_oauth_token = os.environ.get("SLACK_BOT_OAUTH_TOKEN")
slack_app_level_token = os.environ.get("SLACK_APP_LEVEL_TOKEN")
slack_user_oauth_token = os.environ.get("SLACK_USER_OAUTH_TOKEN")


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

    def fetch_thread_messages(self, channel, thread_ts):
        try:
            response = self.web_client.conversations_replies(channel=channel, ts=thread_ts)
            messages = response['messages']
            return messages
        except SlackApiError as e:
            print(f"Error fetching thread messages: {e.response['error']}")
            return None




def test():
    slack_client = SlackClient()
    messages = slack_client.fetch_thread_messages(channel="C06EGCDNA4A", thread_ts="1712443018.659929")
    print(messages)


if __name__ == "__main__":
    slack_bot_user_oauth_token = "xoxb-get_key_from_.env"
    test()
    example_output = [{'user': 'U024UF2F68H', 'type': 'message', 'ts': '1712443018.659929', 'client_msg_id': 'f9b78c94-0f24-4bbc-a204-403f13511c26', 'text': 'This is a simple message on a channel', 'team': 'T02493EGZ4N', 'thread_ts': '1712443018.659929', 'reply_count': 1, 'reply_users_count': 1, 'latest_reply': '1712443121.047909', 'reply_users': ['U024UF2F68H'], 'is_locked': False, 'subscribed': False, 'blocks': [{'type': 'rich_text', 'block_id': 'jdzU7', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'This is a simple message on a channel'}]}]}], 'reactions': [{'name': 'bookmark', 'users': ['U024UF2F68H'], 'count': 1}]}, {'user': 'U024UF2F68H', 'type': 'message', 'ts': '1712443121.047909', 'client_msg_id': 'e838ac8f-a26a-429a-970d-5af7dd4a0abb', 'text': 'this is a reply to the message in thread', 'team': 'T02493EGZ4N', 'thread_ts': '1712443018.659929', 'parent_user_id': 'U024UF2F68H', 'blocks': [{'type': 'rich_text', 'block_id': 'saga/', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'this is a reply to the message in thread'}]}]}], 'reactions': [{'name': 'bookmark', 'users': ['U024UF2F68H'], 'count': 1}]}]
