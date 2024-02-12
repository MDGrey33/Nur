import os
import logging
import requests
from persistqueue import Queue
from file_system.file_manager import FileManager
from database.nur_database import store_pages_data, is_page_processed, get_last_updated_timestamp
from confluence_integration.retrieve_space import process_page, choose_space
from configuration import persist_page_processing_queue_path, persist_page_vector_queue_path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class QueueManager:
    """
    Manages the queue for processing pages.
    """

    def __init__(self, base_path, space_key):
        """
        Initializes the queue manager.
        :param base_path:
        :param space_key:
        """
        self.process_page_queue_path = os.path.join(base_path, space_key)
        self.page_queue = Queue(self.process_page_queue_path)

    def enqueue_page(self, page_id):
        """
        Enqueues a page for processing.
        :param page_id:
        :return:
        """
        self.page_queue.put(page_id)

    def dequeue_page(self):
        """
        Dequeues a page for processing.
        :return:
        """
        if not self.page_queue.empty():
            return self.page_queue.get()
        return None

    def task_done(self):
        """
        Marks the task as done.
        :return:
        """
        self.page_queue.task_done()

    def qsize(self):
        """
        Returns the size of the queue.
        :return:
        """
        return self.page_queue.qsize()


class PageProcessor:
    """
    Processes the pages.
    """

    def __init__(self, file_manager, space_key):
        """
        Initializes the page processor.
        :param file_manager:
        :param space_key:
        """
        self.file_manager = file_manager
        self.space_key = space_key

    def process_page(self, page_id, page_content_map):
        """
        Processes the page.
        :param page_id:
        :param page_content_map:
        :return:
        """
        last_updated_in_db = get_last_updated_timestamp(page_id)
        if last_updated_in_db and not is_page_processed(page_id, last_updated_in_db):
            process_page(page_id, self.space_key, self.file_manager, page_content_map)
        elif not last_updated_in_db:
            process_page(page_id, self.space_key, self.file_manager, page_content_map)


def sumit_embedding_creation_request(page_id):
    endpoint_url = "http://localhost:8000/api/v1/embeds"
    headers = {"Content-Type": "application/json"}
    payload = {"page_id": page_id}

    try:
        response = requests.post(endpoint_url, json=payload, headers=headers)
        response.raise_for_status()  # This will raise for HTTP errors
        logging.info(f"Embedding creation request successful for page ID {page_id}.")
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred while submitting embedding creation request for page ID {page_id}: {e}")
    except Exception as e:
        logging.error(f"An error occurred while submitting embedding creation request for page ID {page_id}: {e}")


def get_page_content_using_queue(space_key):
    logging.info(f"Starting to process pages for space key: {space_key}")
    process_page_queue = QueueManager(persist_page_processing_queue_path, space_key)
    vectorization_queue = QueueManager(persist_page_vector_queue_path, space_key)
    file_manager = FileManager()
    page_content_map = {}
    page_processor = PageProcessor(file_manager, space_key)

    while (page_id := process_page_queue.dequeue_page()) is not None:
        logging.info(f"Processing page with ID {page_id}...")
        page_processor.process_page(page_id, page_content_map)
        vectorization_queue.enqueue_page(page_id)

        process_page_queue.task_done()
        logging.info(f"Page with ID {page_id} processing complete, added for vectorization.")
    # iterate through the page_content_map and call the embed api the IDs list
    page_ids = [page_id for page_id in page_content_map.keys()]
    for page_id in page_ids:
        sumit_embedding_creation_request(page_id)
    logging.info(f"Page content for space key {space_key} processing complete.")
    store_pages_data(space_key, page_content_map)


if __name__ == "__main__":
    space_key = choose_space()
    logging.info(f"Script started for space key: {space_key}")
    get_page_content_using_queue(space_key)
