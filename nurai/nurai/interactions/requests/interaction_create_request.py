from pydantic import BaseModel
from datetime import datetime


class InteractionCreate(BaseModel):
    thread_ts: str
    question_text: str
    assistant_thread_id: str
    answer_text: str
    channel_id: str
    slack_user_id: str
    question_timestamp: datetime
    answer_timestamp: datetime
    comments: str
