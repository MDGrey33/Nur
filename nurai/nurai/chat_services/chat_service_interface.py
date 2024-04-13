# /nurai/services/chat_service_interface.py

from abc import ABC, abstractmethod


class ChatServiceInterface(ABC):
    @abstractmethod
    def start_service(self):
        """
        Starts the chat service. This method should handle all necessary initializations and configurations
        needed to bring the chat service online.
        """
        pass

    @abstractmethod
    def fetch_thread_messages(self, channel, thread_ts):
        """
        Fetches a thread of messages from a chat service based on the given channel and thread timestamp.

        Args:
            channel (str): The identifier for the channel from which to fetch the thread.
            thread_ts (str): The timestamp or identifier of the thread to fetch.

        Returns:
            list: A list of messages, which are typically dictionaries containing message details.
        """
        pass

    @abstractmethod
    def transform_messages_to_interaction_input(self, messages, channel_id):
        """
        Transforms the list of messages fetched from a thread into a structured format suitable for further processing or interaction.

        Args:
            messages (list): A list of message dictionaries fetched from a chat thread.
            channel_id (str): The identifier of the channel where the messages were posted.

        Returns:
            dict or None: A dictionary containing structured interaction data, or None if transformation is not possible.
        """
        pass
