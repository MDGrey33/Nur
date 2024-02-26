# ./database/nur_database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base  # Updated import
import sqlite3
from configuration import sql_file_path
from datetime import datetime, timezone
import json
from functools import wraps
import time
from sqlalchemy.exc import OperationalError, SQLAlchemyError


def retry_on_lock(exception, max_attempts=5, initial_wait=0.5, backoff_factor=2):
    """
    A decorator to retry a database operation in case of a lock.

    Args:
        exception: The exception to catch and retry on.
        max_attempts (int): Maximum number of retry attempts.
        initial_wait (float): Initial wait time between attempts in seconds.
        backoff_factor (int): Factor by which to multiply wait time for each retry.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            wait_time = initial_wait
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    if "database is locked" in str(e):
                        print(f"Database is locked, retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        attempts += 1
                        wait_time *= backoff_factor
                    else:
                        raise
            raise OperationalError("Maximum retry attempts reached, database still locked.")
        return wrapper
    return decorator


# Define the base class for SQLAlchemy models
Base = declarative_base()


class QAInteractions(Base):
    """
    SQLAlchemy model for storing Q&A interactions from Slack.
    """
    __tablename__ = 'qa_interactions'

    interaction_id = Column(Integer, primary_key=True)
    question_text = Column(Text)
    thread_id = Column(String)
    assistant_thread_id = Column(String)
    answer_text = Column(Text)
    channel_id = Column(String)
    question_timestamp = Column(DateTime)
    answer_timestamp = Column(DateTime)
    comments = Column(Text, default=json.dumps([]))  # Set default to an empty JSON array


class QAInteractionManager:
    """
    Manages the storage and retrieval of Q&A interactions from Slack.
    """
    def __init__(self, session):
        self.session = session

    @retry_on_lock(OperationalError)
    def add_question_and_answer(self, question, answer, thread_id, assistant_thread_id, channel_id, question_ts, answer_ts):
        serialized_answer = json.dumps(answer.__dict__) if not isinstance(answer, str) else answer

        # Log the types and values of the parameters
        print(
            f"Inserting into database: question={question}, answer={answer}, thread_id={thread_id}, assistant_thread_id={assistant_thread_id}, channel_id={channel_id}, question_ts={question_ts}, answer_ts={answer_ts}")
        print(
            f"Data types: question={type(question)}, answer={type(answer)}, thread_id={type(thread_id)}, assistant_thread_id={type(assistant_thread_id)}, channel_id={type(channel_id)}, question_ts={type(question_ts)}, answer_ts={type(answer_ts)}")

        interaction = QAInteractions(
            question_text=question,
            thread_id=thread_id,
            assistant_thread_id=assistant_thread_id,
            answer_text=serialized_answer,
            channel_id=channel_id,
            question_timestamp=question_ts,
            answer_timestamp=answer_ts,
            comments=json.dumps([])  # Initialize an empty list of comments
        )
        self.session.add(interaction)
        self.session.commit()

    @retry_on_lock(OperationalError)
    def add_comment_to_interaction(self, thread_id, comment):
        """
        Add a comment to an existing Q&A interaction.
        :param thread_id:
        :param comment:
        :return:
        """
        interaction = self.session.query(QAInteractions).filter_by(thread_id=thread_id).first()
        if interaction:
            if interaction.comments is None:
                interaction.comments = json.dumps([])
            comments = json.loads(interaction.comments)
            comments.append(comment)
            interaction.comments = json.dumps(comments)
            self.session.commit()

    def get_interaction_by_thread_id(self, thread_id):
        return self.session.query(QAInteractions).filter_by(thread_id=thread_id).first()

    def get_qa_interactions(self):
        """
        Retrieve all Q&A interactions.

        Returns:
            list: A list of QAInteractions objects.
        """
        return self.session.query(QAInteractions).all()

    def get_all_interactions(self):
        return self.session.query(QAInteractions).all()


# Set up the database engine and create tables if they don't exist
engine = create_engine('sqlite:///' + sql_file_path)
Base.metadata.bind = engine
Base.metadata.create_all(engine)

# Create a session maker object to manage database sessions
Session = sessionmaker(bind=engine)
session = Session()
