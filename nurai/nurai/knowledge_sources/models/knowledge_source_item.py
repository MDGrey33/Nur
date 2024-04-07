from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime
from sqlalchemy.sql import func

from nurai.database.database import Base, get_db
from nurai.database.mixins.crud_mixin import CRUDMixin


class KnowledgeSourceItem(Base, CRUDMixin):
    __tablename__ = "knowledge_source_item"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("knowledge_source.id"))
    external_identifier = Column(String(256), nullable=False)
    title = Column(String(256), nullable=False)
    file_identifier = Column(String(256), nullable=False)
    author = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    last_processed_at = Column(DateTime, default=None)

    def get_filter_attributes(self):
        return ["source_id", "external_identifier"]
