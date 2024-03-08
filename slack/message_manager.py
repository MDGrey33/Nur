from slack_sdk import WebClient
from credentials import slack_bot_user_oauth_token

from slack_sdk import WebClient
from credentials import slack_bot_user_oauth_token


def post_messages_to_slack(channel_id, message_texts):
    """
    Posts a list of messages to a specified Slack channel.

    Args:
        channel_id (str): The ID of the channel where the messages will be posted.
        message_texts (list of str): The texts of the messages to post.

    Returns:
        list: A list of responses from the Slack API for each posted message.
    """
    # Initialize the Slack client with the bot user OAuth token
    client = WebClient(token=slack_bot_user_oauth_token)

    responses = []

    for message_text in message_texts:
        try:

            # Post each message to the specified channel
            response = client.chat_postMessage(
                channel=channel_id,
                text=message_text,
            )


            # Check if the response indicates a successful post
            if response["ok"]:
                print(f"Message successfully posted to channel {channel_id}")
                responses.append(response)
            else:
                print(f"Failed to post message to channel {channel_id}. Error: {response['error']}")
                responses.append(None)
        except Exception as e:
            print(f"Exception occurred while posting message to Slack: {e}")
            responses.append(None)

    return responses
