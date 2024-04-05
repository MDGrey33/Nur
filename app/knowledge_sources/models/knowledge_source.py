from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from app.database.database import Base
from app.database.mixins.crud_mixin import CRUDMixin
from app.users.models.user import User


class KnowledgeSource(Base, CRUDMixin):
    __tablename__ = "knowledge_source"
    id = Column(Integer, primary_key=True)
    source_type = Column(String(256), nullable=False)
    source_external_name = Column(String(256), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))


    def get_filter_attributes(self):
        return [
            'user_id',
            'source_type'
        ]
