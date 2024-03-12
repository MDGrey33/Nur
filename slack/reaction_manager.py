from slack_sdk.errors import SlackApiError
from database.quiz_question_manager import QuizQuestionManager
from open_ai.chat.format_knowledge_gathering import query_gpt_4t_with_context
import json
import re
from confluence_integration.system_knowledge_manager import create_page_on_confluence

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
    context = ""
    # Check if the reaction is to an item whose timestamp is in the list of timestamps
    if item_ts in timestamps_str:
        print(f'\n The event refers to a knowledge gathering request\n{event}')
        # Print the valid item timestamp to the console
        print(f'\nEvent timestamp: {item_ts}')
        # assign the channel to the channel where the reaction was added
        channel = event.get("item", {}).get("channel")
        knowledge_gathering_messages = get_message_replies(slack_web_client, channel, item_ts)
        for knowledge_gathering_message in knowledge_gathering_messages:
            # generate a string containing all the messages to include as context by appending them all
            context += knowledge_gathering_message.get("text", "")

    _ = ""
    confluence_page_content = query_gpt_4t_with_context(_, context)
    print(f"Confluence page content: {confluence_page_content}")
    # response is: ```json
    # {
    #   "page_title": "Scope of Cloud Native Infrastructure",
    #   "page_content": "Cloud native infrastructure is responsible for managing all aspects of infrastructure on Google Cloud. This includes advising on architecture for cloud-related projects. It is focused solely on technology and does not deal with weather forecasting."
    # }
    # extract the page title and page content from the response into a dictionary
    # Simulating the response from the function, including the triple backticks, "json", and the JSON content

    # Find the position where "json" occurs and add 4 to get the position after "json"
    json_start_pos = confluence_page_content.find('json') + 4

    # Find the position of the first opening curly brace after "json"
    brace_start_pos = confluence_page_content.find('{', json_start_pos)

    json_string = confluence_page_content[brace_start_pos:-3].strip()

    # cleanup json string from escape characters
    cleaned_json_string = re.sub(r'[\x00-\x1F]+', '', json_string)

    # Parse the JSON string into a Python dictionary
    response_dict = json.loads(cleaned_json_string)

    # Extract the page title and content into a new dictionary
    extracted_info = {
        "page_title": response_dict["page_title"],
        "page_content": response_dict["page_content"]
    }

    quiz_question_manager.update_with_summary_by_thread_id(thread_id=item_ts, summary=cleaned_json_string)
    create_page_on_confluence(extracted_info["page_title"], extracted_info["page_content"])
