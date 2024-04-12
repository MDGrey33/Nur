# /nurai/events/routing/events.py
from fastapi import APIRouter
from nurai.events.models.events import (
    QuestionEvent,
    FollowUpEvent,
    ReplyEvent,
    BotQuestionEvent,
    BookmarkEvent,
)
from fastapi import HTTPException
import requests
from nurai.logger.logger import setup_logger

logging = setup_logger()

router = APIRouter()


@router.post("/events/questions")
async def handle_question_event(event: QuestionEvent):
    # Echo back the received event data
    return {"message": "Question event received", "data": event.dict()}


@router.post("/events/follow-ups")
async def handle_follow_up_event(event: FollowUpEvent):
    # Echo back the received event data
    return {"message": "Follow-up event received", "data": event.dict()}


@router.post("/events/replies")
async def handle_reply_event(event: ReplyEvent):
    # Echo back the received event data
    return {"message": "Reply event received", "data": event.dict()}


@router.post("/events/bot-questions")
async def handle_bot_question_event(event: BotQuestionEvent):
    # Echo back the received event data
    return {"message": "Bot question event received", "data": event.dict()}


@router.post("/events/bookmarks")
async def handle_bookmark_event(event: BookmarkEvent):
    logging.info("Received bookmark event: %s", event.dict())

    # Step 1: Fetch the Slack thread
    fetch_url = f"http://127.0.0.1:8000/fetch-slack-thread/?channel={event.channel}&ts={event.ts}"
    try:
        logging.info("Fetching Slack thread from URL: %s", fetch_url)
        fetch_response = requests.get(fetch_url)
        fetch_response.raise_for_status()  # Ensure successful response
        interaction_data = fetch_response.json()
        logging.info("Successfully fetched Slack thread: %s", interaction_data)
    except requests.RequestException as e:
        logging.error("Failed to fetch Slack thread: %s", str(e))
        raise HTTPException(status_code=400, detail=f"Failed to fetch Slack thread: {str(e)}")

    # Step 2: Store the interaction
    create_url = "http://127.0.0.1:8000/interactions/create_or_update/"
    try:
        logging.info("Storing interaction with data: %s", interaction_data)
        create_response = requests.post(create_url, json=interaction_data)
        create_response.raise_for_status()
        logging.info("Successfully stored interaction")
    except requests.RequestException as e:
        logging.error("Failed to store interaction: %s", str(e))
        raise HTTPException(status_code=400, detail=f"Failed to store interaction: {str(e)}")

    logging.info("Bookmark event processed successfully")
    return {"message": "Bookmark event received and processed", "data": event.dict()}