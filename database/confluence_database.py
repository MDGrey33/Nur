# ./database/confluence_database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from configuration import sql_file_path
import sqlite3


# Define the base class for SQLAlchemy models
Base = declarative_base()


# Define the SpaceData model
class SpaceData(Base):
    """
    SQLAlchemy model for storing Confluence space data.
    """
    __tablename__ = 'space_data'

    id = Column(Integer, primary_key=True)
    space_key = Column(String)
    url = Column(String)
    login = Column(String)
    token = Column(String)


# Define the PageData model
class PageData(Base):
    """
    SQLAlchemy model for storing Confluence page data.
    """
    __tablename__ = 'page_data'

    id = Column(Integer, primary_key=True)
    page_id = Column(String)
    space_key = Column(String)
    title = Column(String)
    author = Column(String)
    createdDate = Column(DateTime)
    lastUpdated = Column(DateTime)
    content = Column(Text)
    comments = Column(Text)
    last_embedded = Column(DateTime)
    date_pulled_from_confluence = Column(DateTime)


class PageProgress(Base):
    """
    SQLAlchemy model for storing Confluence page progress.
    """
    __tablename__ = 'page_progress'
    id = Column(Integer, primary_key=True)
    page_id = Column(String, unique=True)
    processed = Column(Boolean, default=False)
    processed_time = Column(DateTime)


def store_space_data(space_data):
    """
    Store Confluence space data into the database.

    Args:
    space_data (dict): A dictionary containing space data to store.
    """
    # Create a new SpaceData object and add it to the session
    new_space = SpaceData(space_key=space_data['space_key'],
                          url=space_data['url'],
                          login=space_data['login'],
                          token=space_data['token'])
    session.add(new_space)
    session.commit()
    print(f"Space with key {space_data['space_key']} written to database")


def parse_datetime(date_string):
    """
    Convert an ISO format datetime string to a datetime object.

    Args:
    date_string (str): ISO format datetime string.

    Returns:
    datetime: A datetime object.
    """
    return datetime.fromisoformat(date_string.replace('Z', '+00:00'))


def store_pages_data(space_key, pages_data):
    """
    Store Confluence page data into the database.

    Args:
    space_key (str): The key of the Confluence space.
    pages_data (dict): A dictionary of page data, keyed by page ID.
    """
    for page_id, page_info in pages_data.items():
        created_date = parse_datetime(page_info['createdDate'])
        last_updated = parse_datetime(page_info['lastUpdated'])
        date_pulled_from_confluence = page_info['datePulledFromConfluence']

        new_page = PageData(page_id=page_id,
                            space_key=space_key,
                            title=page_info['title'],
                            author=page_info['author'],
                            createdDate=created_date,
                            lastUpdated=last_updated,
                            content=page_info['content'],
                            comments=page_info['comments'],
                            date_pulled_from_confluence=date_pulled_from_confluence
                            )
        session.add(new_page)
        print(f"Page with ID {page_id} written to database")
    session.commit()


def get_page_data_from_db():
    # Connect to the SQLite database
    conn = sqlite3.connect(sql_file_path)
    cursor = conn.cursor()

    # Retrieve records from the "page_data" table where "lastUpdated" is newer than "last_embedded"
    cursor.execute("SELECT * FROM page_data WHERE lastUpdated > last_embedded OR last_embedded IS NULL")
    records = cursor.fetchall()

    # Process each record into a string
    all_documents = []
    page_ids = []
    for record in records:
        document = (
            f"Page id: {record[1]}, space key: {record[2]}, title: {record[3]}, "
            f"author: {record[4]}, created date: {record[5]}, last updated: {record[6]}, "
            f"content: {record[7]}, comments: {record[8]}"
        )
        all_documents.append(document)
        page_ids.append(record[1])

    # Close the SQLite connection
    conn.close()
    return all_documents, page_ids


def update_embed_date(page_ids):
    """
    Update the last_embedded timestamp in the database for the given page IDs.
    :param page_ids:
    :return:
    """
    conn = sqlite3.connect(sql_file_path)
    cursor = conn.cursor()
    current_time = datetime.now()
    for page_id in page_ids:
        cursor.execute("UPDATE page_data SET last_embedded = ? WHERE page_id = ?", (current_time, page_id))
    conn.commit()
    conn.close()
    return True


def mark_page_as_processed(page_id):
    """
    Mark a page as processed in the database.
    :param page_id:
    :return:
    """
    session = Session()
    current_time = datetime.now()
    record = session.query(PageProgress).filter_by(page_id=page_id).first()
    if not record:
        record = PageProgress(page_id=page_id, processed=True, processed_time=current_time)
        session.add(record)
    else:
        record.processed = True
        record.processed_time = current_time
    session.commit()
    session.close()
    return True


def is_page_processed(page_id, last_updated):
    """
    Check if a page has already been processed.
    :param page_id:
    :param last_updated:
    :return:
    """
    session = Session()
    record = session.query(PageProgress).filter_by(page_id=page_id).first()
    session.close()
    if record and record.processed:
        return last_updated <= record.processed_time
    return False


def reset_processed_status():
    """
    Reset the processed status of all pages.
    :return:
    """
    session = Session()
    session.query(PageProgress).update({PageProgress.processed: False})
    session.commit()
    session.close()
    return True


def get_last_updated_timestamp(page_id):
    """
    Get the last updated timestamp for a page.
    :param page_id:
    :return:
    """
    session = Session()
    page_record = session.query(PageData).filter_by(page_id=page_id).first()
    session.close()

    if page_record:
        return page_record.lastUpdated
    else:
        return None


# Setup the database engine and create tables if they don't exist
engine = create_engine('sqlite:///' + sql_file_path)
Base.metadata.bind = engine
Base.metadata.create_all(engine)

# Create a sessionmaker object to manage database sessions
Session = sessionmaker(bind=engine)
session = Session()
