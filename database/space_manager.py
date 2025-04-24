# ./database/space_manager.py

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from configuration import sql_file_path


Base = declarative_base()


class SpaceInfo(Base):
    """
    SQLAlchemy model for storing Confluence space data.
    """

    __tablename__ = "space_info"

    id = Column(Integer, primary_key=True)
    space_key = Column(String, nullable=False)
    space_name = Column(String, nullable=False)
    last_import_date = Column(DateTime, nullable=False)


def init_db():
    engine = create_engine("sqlite:///" + sql_file_path)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


class SpaceManager:
    def __init__(self):
        self.session = init_db()

    def add_space_info(self, space_key, space_name, last_import_date):
        """Add a new space to the database."""
        new_space = SpaceInfo(
            space_key=space_key,
            space_name=space_name,
            last_import_date=datetime.strptime(last_import_date, "%Y-%m-%d %H:%M:%S"),
        )
        self.session.add(new_space)
        self.session.commit()

    def update_space_info(self, space_key, last_import_date):
        """Update the last import date of an existing space."""
        space = self.session.query(SpaceInfo).filter_by(space_key=space_key).first()
        if space:
            space.last_import_date = datetime.strptime(
                last_import_date, "%Y-%m-%d %H:%M:%S"
            )
            self.session.commit()
        else:
            print(f"Space with key {space_key} not found.")

    def upsert_space_info(self, space):
        """Insert or update space information based on the existence of the space key."""
        existing_space = (
            self.session.query(SpaceInfo).filter_by(space_key=space.space_key).first()
        )
        if existing_space:
            # The space exists, update the last import date.
            existing_space.last_import_date = datetime.strptime(
                space.last_import_date, "%Y-%m-%d %H:%M:%S"
            )
            operation = "Updated"
        else:
            # The space does not exist, create a new record.
            new_space = SpaceInfo(
                space_key=space.space_key,
                space_name=space.space_name,
                last_import_date=datetime.strptime(
                    space.last_import_date, "%Y-%m-%d %H:%M:%S"
                ),
            )
            self.session.add(new_space)
            operation = "Added"
        self.session.commit()
        return operation

    def list_all_spaces(self):
        """Return all imported spaces as a list of dicts."""
        spaces = self.session.query(SpaceInfo).all()
        return [
            {
                'space_key': s.space_key,
                'space_name': s.space_name,
                'last_import_date': s.last_import_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            for s in spaces
        ]
