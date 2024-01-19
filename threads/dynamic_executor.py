# ./threads/dynamic_executor.py
from concurrent.futures import ThreadPoolExecutor
import queue
from gpt_4t.query_from_documents_threads import get_response_from_gpt_4t


class DynamicExecutor:
    def __init__(self):
        self.executor = ThreadPoolExecutor()
        self.futures = queue.Queue()

    def add_task(self, question, context):
        """Submit a new task to the thread pool and store the future."""
        future = self.executor.submit(get_response_from_gpt_4t, question, context)
        self.futures.put(future)

    def get_next_result(self):
        """Get the result from the next completed future."""
        if self.futures.empty():
            return None  # No tasks are pending
        future = self.futures.get()
        return future.result()  # This will block until the future is complete
