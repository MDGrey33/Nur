# ./database/space_manager.py

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from configuration import sql_file_path
from functools import wraps
import time
from sqlalchemy.exc import OperationalError


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


Base = declarative_base()


class SpaceInfo(Base):
    """
    SQLAlchemy model for storing Confluence space data.
    """
    __tablename__ = 'space_info'

    id = Column(Integer, primary_key=True)
    space_key = Column(String, nullable=False)
    space_name = Column(String, nullable=False)
    last_import_date = Column(DateTime, nullable=False)

def init_db():
    engine = create_engine('sqlite:///' + sql_file_path)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


class SpaceManager:
    def __init__(self):
        self.session = init_db()

    @retry_on_lock(OperationalError)
    def add_space_info(self, space_key, space_name, last_import_date):
        """Add a new space to the database."""
        new_space = SpaceInfo(
            space_key=space_key,
            space_name=space_name,
            last_import_date=datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
        )
        self.session.add(new_space)
        self.session.commit()

    @retry_on_lock(OperationalError)
    def update_space_info(self, space_key, last_import_date):
        """Update the last import date of an existing space."""
        space = self.session.query(SpaceInfo).filter_by(space_key=space_key).first()
        if space:
            space.last_import_date = datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
            self.session.commit()
        else:
            print(f"Space with key {space_key} not found.")

    @retry_on_lock(OperationalError)
    def upsert_space_info(self, space_key, space_name, last_import_date):
        """Insert or update space information based on the existence of the space key."""
        space = self.session.query(SpaceInfo).filter_by(space_key=space_key).first()
        if space:
            # The space exists, update the last import date.
            space.last_import_date = datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
            operation = 'Updated'
        else:
            # The space does not exist, create a new record.
            space = SpaceInfo(
                space_key=space_key,
                space_name=space_name,
                last_import_date=datetime.strptime(last_import_date, '%Y-%m-%d %H:%M:%S')
            )
            self.session.add(space)
            operation = 'Added'
        self.session.commit()
        return operation
