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
from nurai.logger.logger import logging


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
    logging.info(f"Received bookmark event:  {event.dict()}")

    # Step 1: Fetch the chat thread using the new method
    fetch_url = f"http://127.0.0.1:8000/fetch-chat-thread/?service_name={event.service_name}&channel={event.channel}&ts={event.ts}"
    try:
        logging.info(f"Fetching chat thread from URL: {fetch_url}")
        fetch_response = requests.get(fetch_url)
        fetch_response.raise_for_status()  # Ensure successful response
        interaction_data = fetch_response.json()
        logging.info(f"Successfully fetched chat thread: {interaction_data}")
    except requests.RequestException as e:
        logging.error(f"Failed to fetch chat thread: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Failed to fetch chat thread: {str(e)}"
        )

    # Step 2: Store the interaction
    create_url = "http://127.0.0.1:8000/interactions/create_or_update/"
    try:
        logging.info(f"Storing interaction with data: {interaction_data}")
        create_response = requests.post(create_url, json=interaction_data)
        create_response.raise_for_status()
        logging.info("Successfully stored interaction")
    except requests.RequestException as e:
        logging.error(f"Failed to store interaction: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Failed to store interaction: {str(e)}"
        )

    logging.info("Bookmark event processed successfully")
    return {"message": "Bookmark event received and processed", "data": event.dict()}
