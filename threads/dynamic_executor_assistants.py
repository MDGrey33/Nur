# ./threads/dynamic_executor.py
from concurrent.futures import ThreadPoolExecutor
import queue
from oai_assistants.query_assistant_from_documents import query_assistant_with_context


class DynamicExecutor:
    def __init__(self):
        self.executor = ThreadPoolExecutor()
        self.futures = queue.Queue()

    def add_task(self, question, page_ids, thread_id):
        """Submit a new task to the thread pool and store the future."""
        future = self.executor.submit(query_assistant_with_context, question, page_ids, thread_id)
        self.futures.put(future)

    def get_next_result(self):
        """Get the result from the next completed future."""
        if self.futures.empty():
            return None  # No tasks are pending
        future = self.futures.get()
        return future.result()  # This will block until the future is complete
