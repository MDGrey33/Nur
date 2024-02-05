# ./oai_assistants/query_assistant_from_documents.py
from oai_assistants.utility import initiate_client
from oai_assistants.file_manager import FileManager
from oai_assistants.thread_manager import ThreadManager
from oai_assistants.assistant_manager import AssistantManager
from configuration import assistant_id_with_rag
from configuration import file_system_path
import logging

logging.basicConfig(level=logging.DEBUG)


def add_files_to_assistant(assistant, file_ids):
    """
    Adds specified files to the assistant's context for referencing in responses.

    Args:
    assistant (Assistant): The assistant to which files will be added.
    file_ids (list of str): List of file IDs to be added to the assistant.
    """
    client = initiate_client()
    file_manager = FileManager(client)
    assistant_manager = AssistantManager(client)

    for file_id in file_ids:
        chosen_file_path = file_system_path + f"/{file_id}.txt"
        purpose = "assistants"
        uploaded_file_id = file_manager.create(chosen_file_path, purpose)
        print(f"File uploaded successfully with ID: {uploaded_file_id}")

        assistant_manager.add_file_to_assistant(assistant.id, uploaded_file_id)
        print(f"File {chosen_file_path} added to assistant {assistant.id}")


def format_pages_as_context(file_ids, max_length=30000):
    """
    Formats specified files as a context string for referencing in responses,
    ensuring the total context length does not exceed the specified maximum length.

    Args:
        file_ids (list of str): List of file IDs to be formatted as context.
        max_length (int): The maximum length allowed for the context.

    Returns:
        str: The formatted context within the maximum length.
    """
    context = ""
    for file_id in file_ids:
        if len(context) >= max_length:
            # If we've already reached or exceeded the maximum length, stop adding more content.
            break
        chosen_file_path = file_system_path + f"/{file_id}.txt"
        with open(chosen_file_path, 'r') as file:
            file_content = file.read()
            # Check if adding the next file's content will exceed the max length
            title = file_content.split('title: ')[1].split('\n')[0].strip()
            space_key = file_content.split('spaceKey: ')[1].split('\n')[0].strip()
            additional_context = f"\nDocument Title: {title}\nSpace Key: {space_key}\n\n{file_content}"

            if len(context) + len(additional_context) <= max_length:
                context += additional_context
            else:
                # If adding the whole document would exceed the limit,
                # only add as much as possible, then break
                available_space = max_length - len(context) - len(" [Content truncated due to size limit.]")
                context += additional_context[:available_space] + " [Content truncated due to size limit.]"
                break  # Stop adding more content to ensure we respect the maximum length

    return context


def query_assistant_with_context(question, page_ids, thread_id=None):
    """
    Queries the assistant with a specific question, after setting up the necessary context by adding relevant files.

    Args:
    question (str): The question to be asked.
    page_ids (list): A list of page IDs representing the files to be added to the assistant's context.
    thread_id (str, optional): The ID of an existing thread to continue the conversation. Default is None.

    Returns:
    list: A list of messages, including the assistant's response to the question.
    """

    # Initiate the client
    client = initiate_client()
    print(f"Client initiated: {client}\n")
    assistant_manager = AssistantManager(client)
    print(f"Assistant manager initiated: {assistant_manager}\n")
    # Retrieve the assistant instance
    assistant = assistant_manager.load_assistant(assistant_id=assistant_id_with_rag)
    print(f"Assistant loaded: {assistant}\n")

    # Ensure page_ids is a list
    if not isinstance(page_ids, list):
        page_ids = [page_ids]
    print(f"IDs of pages to load in context : {page_ids}\n")

    # Format the context
    context = format_pages_as_context(page_ids)
    print(f"\n\nContext formatted: {context}\n")

    # Initialize ThreadManager with or without an existing thread_id
    thread_manager = ThreadManager(client, assistant.id, thread_id)
    print(f"Thread manager initiated: {thread_manager}\n")
    # If no thread_id was provided, create a new thread
    if thread_id is None:
        thread_manager.create_thread()
        print(f"Thread created: {thread_manager.thread_id}\n")
    else:
        print(f"Thread loaded with the following ID: {thread_id}\n")

    # Format the question with context and query the assistant
    formatted_question = (f"Here is the question and the context\n\n{question}\n\nContext:\n{context}, to request more context, use the get_context tool")
    print(f"Formatted question: {formatted_question}\n")

    # Query the assistant
    messages, thread_id = thread_manager.add_message_and_wait_for_reply(formatted_question, [])
    print(f"The thread_id is: {thread_id}\n Messages received: {messages}\n")
    if messages and messages.data:
        assistant_response = messages.data[0].content[0].text.value
        print(f"Assistant full response: {assistant_response}\n")
    else:
        assistant_response = "No response received."
        print(f"No response received.\n")

    return assistant_response, thread_id


if __name__ == "__main__":
    # First query - introduce a piece of information
    initial_question = "Tell me about Billing cycles"
    initial_response, thread_id = query_assistant_with_context(initial_question, [])

    print("Initial Response:", initial_response)
    print("Thread ID from Initial Query:", thread_id)

