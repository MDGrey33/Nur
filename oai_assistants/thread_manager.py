# ./oai_assistants/thread_manager.py
import time


class ThreadManager:
    """
    Manages threads for asynchronous handling of conversations or operations in the GPT-4-Turbo-Assistant.

    This class provides functionality to create and manage threads, allowing simultaneous operations and
    conversations. It handles adding messages, waiting for replies, checking the status of operations,
    and retrieving and displaying messages within these threads.

    Attributes:
    client (OpenAI_Client): An instance of the client used for handling thread operations.
    """
    def __init__(self, client, assistant_id, thread_id=None):
        """
        Initializes the ThreadManager with a client to manage threads.

        Parameters:
        client (OpenAI_Client): The client object used for thread operations.
        assistant_id (str): The ID of the assistant associated with this thread manager.
        thread_id (str, optional): The identifier of an existing thread to be managed. Default is None.
        """
        self.client = client
        self.assistant_id = assistant_id
        self.thread_id = thread_id

    def create_thread(self):
        """
        Creates a new thread and sets its ID to the thread_id attribute.

        Returns:
        None
        """
        if self.thread_id is None:
            thread = self.client.beta.threads.create()
            self.thread_id = thread.id
            print("\nThread created with ID:", self.thread_id)
        else:
            print("\nThread already initialized with ID:", self.thread_id)

    def add_message_and_wait_for_reply(self, user_message, message_files):
        """
        Adds a message to a thread and waits for the reply.

        Parameters:
        thread_id (str): The ID of the thread to add the message to.
        user_message (str): The message from the user to add to the thread.
        message_files (list): List of file IDs associated with the message.

        Returns:
        list: A list of messages constituting the conversation thread.
        """
        # Add the user's message to the thread
        self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=user_message,
            file_ids=message_files
        )
        print("\nUser message added to thread:", user_message)

        # Request the assistant to process the message
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
        )
        print("\nAssistant requested to process the message.")

        # Wait for a response from the assistant
        run_status = self.check_run_status(run.id)
        while run_status.status != "completed":
            print("Waiting for assistant...")
            time.sleep(20)
            run_status = self.check_run_status(run.id)
            print(f"Run status: {run_status.status}")
        print("\nAssistant run status is [completed].")

        # Retrieve and display the messages
        messages = self.retrieve_messages()
        self.display_messages(messages)
        return messages, self.thread_id

    def check_run_status(self, run_id):
        """
        Checks the status of a thread run.

        Parameters:
        thread_id (str): The ID of the thread to check.

        Returns:
        str: The current status of the thread run.
        """
        return self.client.beta.threads.runs.retrieve(
            thread_id=self.thread_id,
            run_id=run_id
        )

    def retrieve_messages(self):
        """
        Retrieves all messages from the specified thread.

        Parameters:
        thread_id (str): The ID of the thread to retrieve messages from.

        Returns:
        list: A list of messages from the thread.
        """
        return self.client.beta.threads.messages.list(
            thread_id=self.thread_id
        )

    def display_messages(self, messages):
        """
        Displays the messages from a thread.

        Parameters:
        messages (list): A list of messages to be displayed.

        Returns:
        None
        """
        messages_dict = self.get_messages_dict(messages)
        self.print_messages_dict(messages_dict)

    def display_messages_old(self, messages):
        """
        Displays the messages from a thread.

        Parameters:
        messages (list): A list of messages to be displayed.

        Returns:
        None
        """
        for message in messages.data:
            if message.role == "assistant":
                print(f"Assistant: {message.content[0].text.value}")
        print("\nMessages displayed.{message.content[0].text.value}")