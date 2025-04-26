from database.quiz_question_manager import QuizQuestionManager
from open_ai.chat.format_knowledge_gathering import query_gpt_4t_with_context
import json
import re
from confluence_integration.system_knowledge_manager import create_page_on_confluence
from gamification.score_manager import ScoreManager
from slack.event_consumer import get_user_name_from_id
from slack_sdk.errors import SlackApiError
from database.bookmarked_conversation_manager import BookmarkedConversationManager
from slack.message_manager import get_message_replies
from use_cases.conversation_to_document import generate_document_from_conversation
import requests


def get_top_users_by_category(slack_web_client):
    score_manager = ScoreManager()
    categories = ["seeker", "revealer", "luminary"]
    top_users_by_category = {}

    for category in categories:
        top_users = score_manager.get_top_users(category)
        # Fetch user names from Slack and format the user data for posting
        formatted_users = []
        for user in top_users:
            user_name = (
                get_user_name_from_id(slack_web_client, user.slack_user_id)
                or "Unknown User"
            )
            formatted_users.append(
                {"name": user_name, "score": getattr(user, f"{category}_score")}
            )
        top_users_by_category[category] = formatted_users

    return top_users_by_category


def post_top_users_in_categories(slack_web_client, channel):
    # Assuming get_top_users_by_category is implemented elsewhere and returns a dictionary
    # where keys are categories and values are lists of top users (name and score).

    top_users_by_category = get_top_users_by_category(slack_web_client)

    # Format the message
    message_blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*Top 10 Users by Category:*"},
        }
    ]
    for category, users in top_users_by_category.items():
        user_lines = [
            f"{idx + 1}. {user['name']} - {user['score']} points"
            for idx, user in enumerate(users)
        ]
        category_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{category}:*\n" + "\n".join(user_lines),
            },
        }
        message_blocks.append(category_section)

    # Post the message to Slack
    try:
        slack_web_client.chat_postMessage(channel=channel, blocks=message_blocks)
    except SlackApiError as e:
        print(f"Failed to post top users message: {e.response['error']}")


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
        print(f"\n The event refers to a knowledge gathering request\n{event}")
        # Print the valid item timestamp to the console
        print(f"\nEvent timestamp: {item_ts}")
        # assign the channel to the channel where the reaction was added
        channel = event.get("item", {}).get("channel")
        knowledge_gathering_messages = get_message_replies(
            slack_web_client, channel, item_ts
        )

        # Assuming ScoreManager or similar exists for managing scores
        score_manager = ScoreManager()

        # Extract unique user IDs from the replies
        replied_user_ids = set(
            message.get("user")
            for message in knowledge_gathering_messages
            if "user" in message
        )

        # Update luminary score for each user who replied
        for user_id in replied_user_ids:
            score_manager.add_or_update_score(user_id, category="luminary", points=1)

        for knowledge_gathering_message in knowledge_gathering_messages:
            # generate a string containing all the messages to include as context by appending them all
            context += knowledge_gathering_message.get("text", "")

    _ = ""
    confluence_page_content = query_gpt_4t_with_context(_, context)
    print(f"Confluence page content: {confluence_page_content}")

    # Find the position where "json" occurs and add 4 to get the position after "json"
    json_start_pos = confluence_page_content.find("json") + 4

    # Find the position of the first opening curly brace after "json"
    brace_start_pos = confluence_page_content.find("{", json_start_pos)

    json_string = confluence_page_content[brace_start_pos:-3].strip()

    # cleanup json string from escape characters
    cleaned_json_string = re.sub(r"[\x00-\x1F]+", "", json_string)

    # Parse the JSON string into a Python dictionary
    if cleaned_json_string:
        response_dict = json.loads(cleaned_json_string)
    else:
        return

    # Extract the page title and content into a new dictionary
    extracted_info = {
        "page_title": response_dict["page_title"],
        "page_content": response_dict["page_content"],
    }

    quiz_question_manager.update_with_summary_by_thread_id(
        thread_id=item_ts, summary=cleaned_json_string
    )
    create_page_on_confluence(
        extracted_info["page_title"], extracted_info["page_content"]
    )
    # After processing the checkmark reaction, post the top users
    channel = event.get("item", {}).get("channel")  # Assuming this is the channel ID
    post_top_users_in_categories(slack_web_client, channel)


def process_bookmark_added_event(slack_web_client, event):
    print(f"Bookmark reaction event identified:\n{event}")

    # Extract the channel and timestamp (ts) of the message that received the bookmark reaction
    channel = event.get("item", {}).get("channel")
    item_ts = event.get("item", {}).get("ts")

    try:
        # Use the get_message_replies function to fetch the conversation
        bookmarked_conversation_messages = get_message_replies(
            slack_web_client, channel, item_ts
        )

        if bookmarked_conversation_messages:
            # Concatenate all messages in the thread into a single string
            conversation_string = "\n".join(
                [msg.get("text", "") for msg in bookmarked_conversation_messages]
            )
            # POST to the async API endpoint
            response = requests.post(
                "http://localhost:8001/api/v1/bookmark_to_confluence",
                json={"conversation": conversation_string, "thread_id": item_ts}
            )
            print("Bookmark event sent to async endpoint:", response.json())
        else:
            print("No messages found for the bookmarked conversation.")
    except SlackApiError as e:
        print(f"Failed to fetch conversation replies: {e.response['error']}")
