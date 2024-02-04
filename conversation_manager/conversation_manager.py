import os
from uuid import uuid4
from simpleaichat import AIChat
from credentials import oai_api_key


class ConversationManager:
    """
    Manages conversations using the simpleaichat AIChat interface.
    Allows for creating and managing multiple conversation sessions with unique IDs.
    """

    def __init__(self, api_key=oai_api_key):
        """
        Initializes the ConversationManager with an OpenAI API key.
        """
        self.api_key = api_key
        self.conversations = {}

    def create_conversation(self, conversation_id=None, question="", context="You are a helpful assistant."):
        """
        Creates a new conversation session, sends an initial question, and returns the AI's response.
        """
        if conversation_id is None or conversation_id.strip() == "":
            conversation_id = str(uuid4())
            print(f"Generating new conversation ID: {conversation_id}")
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = AIChat(api_key=self.api_key, model="gpt-4-1106-preview",
                                                         system=context, id=conversation_id)
            # Immediately send the initial question if provided and return its response
            if question:
                response = self.conversations[conversation_id](question)
                return conversation_id, response
        else:
            print(f"Conversation with ID {conversation_id} already exists.")
        return conversation_id, None  # Return the ID and None if no question was provided

    def add_message_to_conversation(self, conversation_id, message):
        """
        Adds a message to the specified conversation and returns the AI's response.
        """
        if conversation_id in self.conversations:
            try:
                response = self.conversations[conversation_id](message)
                return response
            except Exception as e:
                print(f"Error during message addition: {e}")
        else:
            raise ValueError("Conversation ID not found")


if __name__ == "__main__":
    # Example usage
    manager = ConversationManager()

    # Create a new conversation with an optional custom ID
    conversation_id = manager.create_conversation("TopAssistTest1")
    print(f"Conversation ID: {conversation_id}")

    # Add a message to the conversation and print the response
    try:
        response = manager.add_message_to_conversation(conversation_id, "Hello, how are you?")
        print("AI Response:", response)
    except ValueError as e:
        print(e)
