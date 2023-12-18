# page_processor.py

from persistqueue import Queue
import os
from file_system.file_manager import FileManager
from database.confluence_database import store_pages_data, is_page_processed, get_last_updated_timestamp
from confluence_integration.retrieve_space import process_page, choose_space
from configuration import persist_page_processing_queue_path


def get_page_content_using_queue(space_key):
    """
    Dequeues and processes pages from the queue.
    """
    queue_path = os.path.join(persist_page_processing_queue_path, space_key)
    page_queue = Queue(queue_path)
    file_manager = FileManager()
    page_content_map = {}
    # Add a counter to track the number of pages processed
    counter = 0

    while not page_queue.empty():
        page_id = page_queue.get()
        counter += 1
        print(f"Processing page with ID {page_id}...")

        last_updated_in_db = get_last_updated_timestamp(page_id)
        if last_updated_in_db and not is_page_processed(page_id, last_updated_in_db):
            process_page(page_id, space_key, file_manager, page_content_map)
        elif not last_updated_in_db:
            process_page(page_id, space_key, file_manager, page_content_map)

        # Mark the page as processed
        page_queue.task_done()
        print(f"Page with ID {page_id} processing complete.")

    # Store all page data in the database
    store_pages_data(space_key, page_content_map)
    print(f"Page content for {counter} pages, writing to individual files and database complete.")


if __name__ == "__main__":
    space_key = choose_space()
    get_page_content_using_queue(space_key)
