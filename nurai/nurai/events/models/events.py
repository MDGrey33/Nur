# ./nurai/events/models/events.py
from pydantic import BaseModel, Field
from typing import Optional


class BaseEventModel(BaseModel):
    ts: str
    thread_ts: Optional[str] = None
    channel: str
    user: str


class QuestionEvent(BaseEventModel):
    text: str
    bot_mention: bool = Field(default=True)
    thread_ts: Optional[str] = None


class FollowUpEvent(BaseEventModel):
    text: str
    bot_mention: bool = Field(default=True)


class ReplyEvent(BaseEventModel):
    text: str
    channel_message: bool = Field(default=True)


class BotQuestionEvent(BaseEventModel):
    text: str
    user_id: str
    contains_question: bool = Field(default=True)


class BookmarkEvent(BaseModel):
    service_name: str
    channel: str
    ts: str
