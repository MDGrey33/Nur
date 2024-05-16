# /nurai/interactions/models/interaction.py
from sqlalchemy import Column, Integer, String, DateTime, Text, func
from nurai.database.database import Base
from nurai.database.mixins.crud_mixin import CRUDMixin


class Interaction(Base, CRUDMixin):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True)
    thread_ts = Column(String(255), index=True)  # Specify length here
    question_text = Column(Text)
    assistant_thread_id = Column(String(255), index=True)  # And here
    answer_text = Column(Text)
    channel_id = Column(String(255))  # Also here
    slack_user_id = Column(String(255))  # Don't forget this one
    question_timestamp = Column(DateTime, default=func.now())
    answer_timestamp = Column(DateTime)
    comments = Column(Text)

    def get_filter_attributes(self):
        """
        Override the method to return 'thread_ts' as the unique identifier for an interaction.
        """
        return ["thread_ts"]
