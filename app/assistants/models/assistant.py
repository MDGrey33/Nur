from typing import List, Dict, Any
from app.database.database import Base
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

from app.database.mixins.crud_mixin import CRUDMixin


class Assistant(Base, CRUDMixin):
    __tablename__ = "assistants"
    id = Column(String(256), primary_key=True)
    created_at = Column(Integer)
    description = Column(String(256))
    file_ids = Column(JSON)
    instructions = Column(String(256))
    external_metadata = Column(JSON)
    model = Column(String(256))
    name = Column(String(256))
    object = Column(String(256))
    tools = Column(JSON)

    def get_filter_attributes(self):
        return [
            'id',
        ]