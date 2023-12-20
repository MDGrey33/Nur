# ./slack/channel_reaction.py
from persistqueue import Queue
import os
from database.confluence_database import get_page_data_by_ids
from configuration import persist_page_vector_queue_path
from vector.chroma import vectorize_documents
from confluence_integration.retrieve_space import choose_space
from confluence_integration.confluence_client import ConfluenceClient


# Main processing function for the vectorization queue
def process_vectorization_queue(space_key):
    queue_path = os.path.join(persist_page_vector_queue_path, space_key)
    vectorization_queue = Queue(queue_path)

    while not vectorization_queue.empty():
        page_id = vectorization_queue.get()

        # Fetch data for the specific page
        all_documents, retrieved_page_ids = get_page_data_by_ids([page_id])
        if all_documents:
            vectorize_documents(all_documents, retrieved_page_ids)

        vectorization_queue.task_done()
        print(f"Page with ID {page_id} vectorization complete.")

    print("Vectorization process complete for all queued pages.")


if __name__ == '__main__':
    confluence_client = ConfluenceClient()
    space_key = choose_space()
    process_vectorization_queue(space_key)
