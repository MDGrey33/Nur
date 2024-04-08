from sqlalchemy import Column, Integer, String, DateTime, func
from nurai.database.database import Base
from nurai.database.mixins.crud_mixin import CRUDMixin


class Interaction(Base, CRUDMixin):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True)
    ts = Column(String, index=True)
    thread_ts = Column(String, index=True, nullable=True)
    channel = Column(String)
    user = Column(String)
    reaction = Column(String)

    def get_filter_attributes(self):
        return ["ts", "channel", "user", "reaction"]
