# events/event_routes.py
from fastapi import APIRouter
from nurai.events.models.events import (
    QuestionEvent,
    FollowUpEvent,
    ReplyEvent,
    BotQuestionEvent,
    CheckmarkEvent,
    BookmarkEvent,
)

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
    # Echo back the received event data
    return {"message": "Bookmark event received", "data": event.dict()}
