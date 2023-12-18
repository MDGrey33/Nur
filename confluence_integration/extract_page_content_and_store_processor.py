# ./confluence_integration/extract_page_content_and_store_processor.py
from persistqueue import Queue
import os
from file_system.file_manager import FileManager
from database.confluence_database import store_pages_data, is_page_processed, get_last_updated_timestamp
from confluence_integration.retrieve_space import process_page, choose_space
from configuration import persist_page_processing_queue_path, persist_page_vector_queue_path


def get_page_content_using_queue(space_key):
    """
    Dequeues and processes pages from the queue.
    """
    # Initializing queue for confluence content extraction
    process_page_queue_path = os.path.join(persist_page_processing_queue_path, space_key)
    page_queue = Queue(process_page_queue_path)

    # Initializing queue for confluence page vectorization
    vectorization_queue_path = os.path.join(persist_page_vector_queue_path, space_key)
    vectorization_queue = Queue(vectorization_queue_path)

    file_manager = FileManager()
    page_content_map = {}
    # Add a counter to track the number of pages processed
    processed_page_counter = 0
    all_page_ids = []
    while not page_queue.empty():
        page_id = page_queue.get()
        processed_page_counter += 1
        print(f"Processing page with ID {page_id}...")

        last_updated_in_db = get_last_updated_timestamp(page_id)
        if last_updated_in_db and not is_page_processed(page_id, last_updated_in_db):
            process_page(page_id, space_key, file_manager, page_content_map)
        elif not last_updated_in_db:
            process_page(page_id, space_key, file_manager, page_content_map)
        all_page_ids.append(page_id)
        # Enqueue the page_id for vectorization
        vectorization_queue.put(page_id)

        # Mark the page as processed
        page_queue.task_done()
        print(f"Page with ID {page_id} processing complete, added for vectorization.")
    print(all_page_ids)
    # Store all page data in the database
    store_pages_data(space_key, page_content_map)
    print(f"Page content for {processed_page_counter} pages, writing to individual files and database complete, added for vectorization.")
    return space_key


if __name__ == "__main__":
    space_key = choose_space()
    get_page_content_using_queue(space_key)
