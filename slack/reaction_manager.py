from slack_sdk.errors import SlackApiError
from database.quiz_question_manager import QuizQuestionManager


def get_message_replies(client, channel, ts):
    """
    Retrieve all replies to a specific message in a Slack channel.

    Parameters:
    - token (str): Your Slack API token.
    - channel (str): The ID of the channel containing the original message.
    - ts (str): The timestamp of the original message.

    Returns:
    - A list of replies to the message, or an error message if the API call fails.
    """

    try:
        # Call the conversations.replies API method
        response = client.conversations_replies(channel=channel, ts=ts)
        replies = response.get('messages', [])

        # Filter out the original message, leaving only the replies
        replies_without_original = [message for message in replies if message['ts'] != ts]

        return replies

    except SlackApiError as e:
        print(f"Slack API Error: {e.response['error']}")
        return []


def process_checkmark_added_event(slack_web_client, event):
    print(f"Reaction event identified:\n{event}")

    quiz_question_manager = QuizQuestionManager()
    timestamps = quiz_question_manager.get_unposted_questions_timestamps()
    # Convert timestamps to strings, as Slack timestamps are string values
    timestamps_str = [str(ts) for ts in timestamps]
    # Extract the timestamp of the item to which the reaction was added
    item_ts = event.get("item", {}).get("ts")

    # Check if the reaction is to an item whose timestamp is in the list of timestamps
    if item_ts in timestamps_str:
        print(f'\n The event refers to a knowledge gathering request\n{event}')
        # Print the valid item timestamp to the console
        print(f'\nEvent timestamp: {item_ts}')
        # assign the channel to the channel where the reaction was added
        channel = event.get("item", {}).get("channel")
        interaction_messages = get_message_replies(slack_web_client, channel, item_ts)
        for interaction_message in interaction_messages:
            print(interaction_message['text'])
