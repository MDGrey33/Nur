from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from configuration import sql_file_path
from database.bookmarked_conversation import BookmarkedConversation, Base
from datetime import datetime, timezone

class BookmarkedConversationManager:
    def __init__(self):
        self.engine = create_engine('sqlite:///' + sql_file_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_bookmarked_conversation(self, title, body, thread_id):
        try:
            with self.Session() as session:
                new_conversation = BookmarkedConversation(title=title, body=body, thread_id=thread_id)
                session.add(new_conversation)
                session.commit()
                return new_conversation.id
        except SQLAlchemyError as e:
            print(f"Error adding bookmarked conversation: {e}")
            return None

    def update_posted_on_confluence(self, conversation_id):
        try:
            with self.Session() as session:
                conversation = session.query(BookmarkedConversation).filter_by(id=conversation_id).first()
                if conversation:
                    conversation.posted_on_confluence = datetime.now(timezone.utc)
                    session.commit()
        except SQLAlchemyError as e:
            print(f"Error updating conversation with Confluence timestamp: {e}")

    def get_unposted_conversations(self):
        try:
            with self.Session() as session:
                return session.query(BookmarkedConversation).filter_by(posted_on_confluence=None).all()
        except SQLAlchemyError as e:
            print(f"Error getting unposted conversations: {e}")
            return None