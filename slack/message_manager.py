# ./slack/message_manager.py
from slack_sdk import WebClient
from credentials import slack_bot_user_oauth_token
from database.quiz_question_manager import QuizQuestionManager
from interactions.quiz_question_dto import QuizQuestionDTO


def post_questions_to_slack(channel_id, quiz_question_dtos):
    """
    Posts a list of QuizQuestionDTO objects to a specified Slack channel.

    Args:
        channel_id (str): The ID of the channel where the messages will be posted.
        quiz_questions (list of QuizQuestionDTO): The QuizQuestionDTO objects to post.

    Returns:
        list: A list of responses from the Slack API for each posted message.
    """
    client = WebClient(token=slack_bot_user_oauth_token)
    responses = []
    quizz_question_manager = QuizQuestionManager()

    for quiz_question_dto in quiz_question_dtos:
        message_text = f"Question: {quiz_question_dto.question_text}"
        try:
            response = client.chat_postMessage(channel=channel_id, text=message_text)
            quiz_question_dto.thread_id = response["ts"]

            quizz_question_manager.update_with_thread_id(
                question_id=quiz_question_dto.id,
                thread_id=quiz_question_dto.thread_id
            )
        except Exception as e:
            print(f"Exception occurred while posting message to Slack: {e}")
            responses.append(None)

    return quiz_question_dtos