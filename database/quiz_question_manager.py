from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from configuration import sql_file_path
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()


class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'
    id = Column(Integer, primary_key=True)
    question_text = Column(Text)
    thread_id = Column(String)  # Slack thread ID for tracking conversations
    summary = Column(Text)  # Summary of the conversation
    posted_on_slack = Column(DateTime)  # Timestamp when posted on Slack
    posted_on_confluence = Column(DateTime, nullable=True)  # Timestamp when posted on Confluence


class QuizQuestionManager:
    def __init__(self):
        # Initialize the database engine
        self.engine = create_engine('sqlite:///' + sql_file_path)
        Base.metadata.create_all(self.engine)  # Create tables if they don't exist
        self.Session = sessionmaker(bind=self.engine)

    def add_quiz_question(self, question_text):
        try:
            with self.Session() as session:
                new_question = QuizQuestion(question_text=question_text, posted_on_slack=datetime.now(timezone.utc))
                session.add(new_question)
                session.commit()
                return new_question.id
        except SQLAlchemyError as e:
            print(f"Error adding quiz question: {e}")
            # Optionally, re-raise the exception if you want to handle it further up the call stack

    def update_with_summary(self, question_id, summary):
        try:
            with self.Session() as session:
                question = session.query(QuizQuestion).filter_by(id=question_id).first()
                if question:
                    question.summary = summary
                    session.commit()
        except SQLAlchemyError as e:
            print(f"Error updating quiz question with summary: {e}")

    def update_with_thread_id(self, question_id, thread_id):
        try:
            with self.Session() as session:
                question = session.query(QuizQuestion).filter_by(id=question_id).first()
                if question:
                    question.thread_id = thread_id
                    question.posted_on_slack = datetime.now(timezone.utc)
                    session.commit()
        except SQLAlchemyError as e:
            print(f"Error updating quiz question with thread ID: {e}")

    def update_confluence_timestamp(self, question_id):
        try:
            with self.Session() as session:
                question = session.query(QuizQuestion).filter_by(id=question_id).first()
                if question:
                    question.posted_on_confluence = datetime.now(timezone.utc)
                    session.commit()
        except SQLAlchemyError as e:
            print(f"Error updating Confluence timestamp: {e}")


# Example usage
if __name__ == "__main__":
    qzm = QuizQuestionManager()
    question_id = qzm.add_quiz_question("What is the airspeed velocity of an unladen swallow?")
    print(f"Added question with ID: {question_id}")