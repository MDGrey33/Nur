import os
import logging
from persistqueue import Queue
from file_system.file_manager import FileManager
from database.nur_database import store_pages_data, is_page_processed, get_last_updated_timestamp
from confluence_integration.retrieve_space import process_page
from configuration import persist_page_processing_queue_path, persist_page_vector_queue_path
from confluence_integration.retrieve_space import choose_space

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_page_content_using_queue(space_key):
    """
    Dequeues and processes pages from the queue.
    """

    logging.info(f"Starting to process pages for space key: {space_key}")
    # Initializing queue for confluence content extraction
    process_page_queue_path = os.path.join(persist_page_processing_queue_path, space_key)
    page_queue = Queue(process_page_queue_path)
    logging.debug(f"Process page queue path: {process_page_queue_path}")

    # Inspect and log the length of the queue
    queue_length = page_queue.qsize()
    logging.info(f"Queue length for space key {space_key}: {queue_length} pages")

    # Initializing queue for confluence page vectorization
    vectorization_queue_path = os.path.join(persist_page_vector_queue_path, space_key)
    vectorization_queue = Queue(vectorization_queue_path)
    logging.debug(f"Vectorization queue path: {vectorization_queue_path}")

    file_manager = FileManager()
    page_content_map = {}
    processed_page_counter = 0
    all_page_ids = []
    while not page_queue.empty():
        page_id = page_queue.get()
        processed_page_counter += 1
        logging.info(f"Processing page with ID {page_id}...")

        last_updated_in_db = get_last_updated_timestamp(page_id)
        if last_updated_in_db and not is_page_processed(page_id, last_updated_in_db):
            process_page(page_id, space_key, file_manager, page_content_map)
        elif not last_updated_in_db:
            process_page(page_id, space_key, file_manager, page_content_map)
        all_page_ids.append(page_id)

        vectorization_queue.put(page_id)
        page_queue.task_done()
        logging.info(f"Page with ID {page_id} processing complete, added for vectorization.")

    logging.info(all_page_ids)
    store_pages_data(space_key, page_content_map)
    logging.info(f"Page content for {processed_page_counter} pages, writing to individual files and database complete, added for vectorization.")
    return space_key

if __name__ == "__main__":
    space_key = choose_space()
    logging.info(f"Script started for space key: {space_key}")
    get_page_content_using_queue(space_key)
