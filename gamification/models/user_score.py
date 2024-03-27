from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from configuration import sql_file_path

Base = declarative_base()


class UserScore(Base):
    __tablename__ = "user_scores"
    id = Column(Integer, primary_key=True)
    slack_user_id = Column(String, unique=True, nullable=False)
    seeker_score = Column(Integer, default=0)
    revealer_score = Column(Integer, default=0)
    luminary_score = Column(Integer, default=0)
