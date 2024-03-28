from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.users.models.user import User


class KnowledgeSource(Base):
    __tablename__ = "knowledge_source"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    source_type = Column(Integer)