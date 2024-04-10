# /nurai/interactions/models/interaction.py
from sqlalchemy import Column, Integer, String, DateTime, Text, func
from nurai.database.database import Base
from nurai.database.mixins.crud_mixin import CRUDMixin


class Interaction(Base, CRUDMixin):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True)
    thread_ts = Column(String, index=True)
    question_text = Column(Text)
    assistant_thread_id = Column(String, index=True)
    answer_text = Column(Text)
    channel_id = Column(String)
    slack_user_id = Column(String)
    question_timestamp = Column(DateTime, default=func.now())
    answer_timestamp = Column(DateTime)
    comments = Column(Text)

    def get_filter_attributes(self):
        return ["question_text", "thread_id", "assistant_thread_id", "answer_text", "channel_id", "slack_user_id",
                "question_timestamp", "answer_timestamp", "comments"]
