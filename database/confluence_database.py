from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from configuration import sql_file_path

# Define the base class for SQLAlchemy models
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


# Setup the database engine and create tables if they don't exist
engine = create_engine('sqlite:///' + sql_file_path)
Base.metadata.bind = engine
Base.metadata.create_all(engine)

# Create a sessionmaker object to manage database sessions
Session = sessionmaker(bind=engine)


def parse_datetime(date_string):
    return datetime.fromisoformat(date_string.replace('Z', '+00:00'))


def store_space_data(space_data):
    session = Session()
    new_space = SpaceData(space_key=space_data['space_key'],
                          url=space_data['url'],
                          login=space_data['login'],
                          token=space_data['token'])
    session.add(new_space)
    session.commit()
    session.close()
    print(f"Space with key {space_data['space_key']} written to database")


def store_pages_data(space_key, pages_data):
    session = Session()
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
    session.close()
    print(f"Pages from space {space_key} written to database")


def store_page_data(page_id, space_key, page_data):
    session = Session()
    created_date = parse_datetime(page_data['createdDate'])
    last_updated = parse_datetime(page_data['lastUpdated'])
    new_page = PageData(page_id=page_id,
                        space_key=space_key,
                        title=page_data['title'],
                        author=page_data['author'],
                        createdDate=created_date,
                        lastUpdated=last_updated,
                        content=page_data['content'],
                        comments=page_data['comments'])

    session.add(new_page)
    session.commit()
    session.close()
    print(f"Page with ID {page_id} written to database")
