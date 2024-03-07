from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from configuration import sql_file_path

# Define the base class for SQLAlchemy models
Base = declarative_base()


class SlackMessageDeduplication(Base):
    """
    SQLAlchemy model for storing deduplication data for Slack messages to prevent reprocessing.
    """
    __tablename__ = 'slack_message_deduplication'

    id = Column(Integer, primary_key=True)
    channel_id = Column(String, nullable=False)  # Identifier for the Slack channel.
    message_ts = Column(String, nullable=False, unique=True)  # Timestamp of the message, unique within a channel.

    def __repr__(self):
        return f"<SlackMessageDeduplication(channel_id='{self.channel_id}', message_ts='{self.message_ts}')>"


# Set up the database engine and create tables if they don't exist
engine = create_engine('sqlite:///' + sql_file_path)
Base.metadata.bind = engine
Base.metadata.create_all(engine)

# Create a session maker object to manage database sessions
Session = sessionmaker(bind=engine)
session = Session()