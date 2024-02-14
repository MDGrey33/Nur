# ./confluence_integration/extract_page_content_and_store_processor.py
import os
import requests
from persistqueue import Queue
from file_system.file_manager import FileManager
from database.nur_database import store_pages_data, is_page_processed, get_last_updated_timestamp
from confluence_integration.retrieve_space import process_page
from configuration import persist_page_processing_queue_path, persist_page_vector_queue_path
from database.nur_database import get_page_ids_missing_embeds
import time
import logging

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


def embed_pages_missing_embeds(retry_limit: int = 3, wait_time: int = 30) -> None:
    for attempt in range(retry_limit):
        # Retrieve the IDs of pages that are still missing embeddings.
        page_ids = get_page_ids_missing_embeds()

        # If there are no pages missing embeddings, exit the loop and end the process.
        if not page_ids:
            print("All pages have embeddings. Process complete.")
            return

        print(f"Attempt {attempt + 1} of {retry_limit}: Processing {len(page_ids)} pages missing embeddings.")
        for page_id in page_ids:
            # Submit a request to generate an embedding for each page ID.
            sumit_embedding_creation_request(page_id)
            # A brief delay between requests to manage load and potentially avoid rate limiting.
            time.sleep(0.5)

        print(f"Waiting for {wait_time} seconds for embeddings to be processed...")
        time.sleep(wait_time)

        # After waiting, retrieve the list of pages still missing embeddings to see if the list has decreased.
        # This retrieval is crucial to ensure that the loop only continues if there are still pages that need processing.
        page_ids = get_page_ids_missing_embeds()
        if not page_ids:
            print("All pages now have embeddings. Process complete.")
            break  # Break out of the loop if there are no more pages missing embeddings.

        print(f"After attempt {attempt + 1}, {len(page_ids)} pages are still missing embeds.")

    # After exhausting the retry limit, check if there are still pages without embeddings.
    if page_ids:
        print("Some pages still lack embeddings after all attempts.")
    else:
        print("All pages now have embeddings. Process complete.")


if __name__ == "__main__":
    embed_pages_missing_embeds()

    '''
    space_key = choose_space()
    logging.info(f"Script started for space key: {space_key}")
    get_page_content_using_queue(space_key)
    '''

