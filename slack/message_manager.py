# ./slack/message_manager.py
from slack_sdk import WebClient
from credentials import slack_bot_user_oauth_token
from database.quiz_question_manager import QuizQuestionManager
from interactions.quiz_question_dto import QuizQuestionDTO

# Assuming the ScoreManager class and add_or_update_score method exist
from gamification.score_manager import ScoreManager
from slack_sdk.errors import SlackApiError


def post_questions_to_slack(channel_id, quiz_question_dtos, user_ids):
    """
    Posts a list of QuizQuestionDTO objects to a specified Slack channel, tags all users in the first reply,
    invites them to contribute to the information gathering related to their questions, asks them to tag domain
    experts or share the question link, and reminds them to mark the questions with a check mark when addressed.

    Args:
        channel_id (str): The ID of the channel where the messages will be posted.
        quiz_question_dtos (list of QuizQuestionDTO): The QuizQuestionDTO objects to post.
        user_ids (list of str): The Slack user IDs to be mentioned in the follow-up message.

    Returns:
        list: A list of QuizQuestionDTOs with their respective thread IDs updated based on the Slack API responses.
    """

    client = WebClient(token=slack_bot_user_oauth_token)
    quiz_question_manager = QuizQuestionManager()
    score_manager = ScoreManager()  # Initialize the ScoreManager

    for quiz_question_dto in quiz_question_dtos:
        try:
            # Post the original question
            response = client.chat_postMessage(
                channel=channel_id, text=f"Question: {quiz_question_dto.question_text}"
            )
            quiz_question_dto.thread_id = response["ts"]

            # Update the thread ID in the database
            quiz_question_manager.update_with_thread_id(
                question_id=quiz_question_dto.id, thread_id=quiz_question_dto.thread_id
            )

            # Construct the follow-up message with user mentions
            user_mentions = " ".join([f"<@{user_id}>" for user_id in user_ids])
            follow_up_message = (
                f"{user_mentions} Please contribute to the information gathering for the above question. "
                "Feel free to tag domain experts, share the question link to relevant channels, "
                "and mark the question with a :white_check_mark: once you believe it has been satisfactorily addressed."
            )

            # Post the follow-up message in a thread
            client.chat_postMessage(
                channel=channel_id,
                text=follow_up_message,
                thread_ts=quiz_question_dto.thread_id,
            )

            # Award points to each revealer
            for user_id in user_ids:
                score_manager.add_or_update_score(
                    user_id, category="revealer", points=1
                )

        except Exception as e:
            print(f"Exception occurred while posting message to Slack: {e}")

    return quiz_question_dtos


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
        replies = response.get("messages", [])

        # Filter out the original message, leaving only the replies
        replies_without_original = [
            message for message in replies if message["ts"] != ts
        ]

        return replies

    except SlackApiError as e:
        print(f"Slack API Error: {e.response['error']}")
        return []
