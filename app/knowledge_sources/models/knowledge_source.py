from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base, get_db
from app.database.mixins.crud_mixin import CRUDMixin
from app.users.models.user import User


class KnowledgeSource(Base, CRUDMixin):
    __tablename__ = "knowledge_source"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    source_type = Column(Integer)

    def get_filter_attributes(self):
        return [
            'user_id',
            'source_type'
        ]
