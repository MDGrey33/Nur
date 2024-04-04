from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func

from app.database.database import Base
from app.database.mixins.crud_mixin import CRUDMixin


class Task(Base, CRUDMixin):
    WAITING = "waiting"
    PROCESSING = "processing"
    FAILED = "failed"
    DONE = "done"

    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    status = Column(String(length=256), default=WAITING)
    start_date = Column(DateTime, default=func.now())
    end_date = Column(DateTime, default=None)

    def get_filter_attributes(self):
        return [
            'id'
        ]
