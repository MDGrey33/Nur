from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.nur_database import PageData, Base
from configuration import sql_file_path
import os

# Setup the database engine
engine = create_engine('sqlite:///' + sql_file_path)
Base.metadata.bind = engine

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Query for unique space keys
spaces = session.query(PageData.space_key).distinct()

# Directory to save the documents
output_directory = 'content/page_title_list'
os.makedirs(output_directory, exist_ok=True)

# For each space, get page titles and write to a document
for space in spaces:
    space_key = space.space_key
    titles = session.query(PageData.title).filter(PageData.space_key == space_key).all()

    # Writing header and titles to a document
    file_path = os.path.join(output_directory, f"{space_key}_titles.txt")
    with open(file_path, "w") as file:
        header = f"This document contains the titles of all the pages in the space '{space_key}'. It is here to assist generating the relevant queries to retrieve context.\n\n"
        file.write(header)
        for title in titles:
            file.write(title.title + "\n")

# Close the session
session.close()

print("Documents generated for each space.")
