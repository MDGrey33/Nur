from confluence_integration.retrieve_space import get_space_content
from confluence_integration.extract_page_content_and_store_processor import (
    get_page_content_using_queue,
)
from confluence_integration.extract_page_content_and_store_processor import (
    embed_pages_missing_embeds,
)
from database.space_manager import SpaceManager
from vector.create_vector_db import add_embeds_to_vector_db
from datetime import datetime


class Space:
    def __init__(self, space_key="", space_name="", last_import_date=""):
        self.space_key = space_key
        self.space_name = space_name
        self.last_import_date = last_import_date

    def load_new(self, space_key, space_name):
        self.space_key = space_key
        self.space_name = space_name
        print("Retrieving space content...")
        get_space_content(space_key)
        get_page_content_using_queue(space_key)
        embed_pages_missing_embeds()
        space_manager = SpaceManager()
        self.last_import_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        space_manager.upsert_space_info(self)
        add_embeds_to_vector_db(space_key)
        print(f"\nSpace '{space_name}' retrieval and indexing complete.")
