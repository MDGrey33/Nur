# ./database/confluence_database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from configuration import sql_file_path


# Define the base class
Base = declarative_base()


# Define the SpaceData model
class SpaceData(Base):
    __tablename__ = 'space_data'

    id = Column(Integer, primary_key=True)
    space_key = Column(String)
    url = Column(String)
    login = Column(String)
    token = Column(String)


# Define the PageData model
class PageData(Base):
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


# Setup database connection
engine = create_engine('sqlite:///' + sql_file_path)
Base.metadata.bind = engine
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def store_space_data(space_data):
    new_space = SpaceData(space_key=space_data['space_key'],
                          url=space_data['url'],
                          login=space_data['login'],
                          token=space_data['token'])
    session.add(new_space)
    session.commit()
    print(f"Space data written to database")


def parse_datetime(date_string):
    return datetime.fromisoformat(date_string.replace('Z', '+00:00'))


def store_pages_data(space_key, pages_data):
    for page_id, page_info in pages_data.items():
        created_date = parse_datetime(page_info['createdDate'])
        last_updated = parse_datetime(page_info['lastUpdated'])

        new_page = PageData(page_id=page_id,
                            space_key=space_key,
                            title=page_info['title'],
                            author=page_info['author'],
                            createdDate=created_date,
                            lastUpdated=last_updated,
                            content=page_info['content'],
                            comments=page_info['comments'])
        session.add(new_page)
    session.commit()
    print("Page content written to database.")


