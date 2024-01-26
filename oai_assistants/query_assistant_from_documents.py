# ./oai_assistants/query_assistant_from_documents.py
from oai_assistants.utility import initiate_client
from oai_assistants.file_manager import FileManager
from oai_assistants.thread_manager import ThreadManager
from oai_assistants.assistant_manager import AssistantManager
from configuration import assistant_id, file_system_path
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


def format_pages_as_context(file_ids):
    """
    Formats specified files as a context string for referencing in responses.

    Args:
    file_ids (list of str): List of file IDs to be formatted as context.

    Returns:
    str: The formatted context.
    """
    context = ""
    for file_id in file_ids:
        chosen_file_path = file_system_path + f"/{file_id}.txt"
        with open(chosen_file_path, 'r') as file:
            file_content = file.read()
            title = file_content.split('title: ')[1].split('\n')[0].strip()
            space_key = file_content.split('spaceKey: ')[1].split('\n')[0].strip()

            context += f"\nDocument Title: {title}\nSpace Key: {space_key}\n\n"
            context += file_content

        print(f"File {file_id} (Title: {title}, Space Key: {space_key}) appended to context successfully")

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
    assistant_manager = AssistantManager(client)

    # Create or retrieve the assistant instance
    assistant = assistant_manager.load_assistant(assistant_id=assistant_id)

    # Ensure page_ids is a list
    if not isinstance(page_ids, list):
        page_ids = [page_ids]

    # Format the context
    context = format_pages_as_context(page_ids)

    # Initialize ThreadManager with or without an existing thread_id
    thread_manager = ThreadManager(client, assistant.id, thread_id)

    # If no thread_id was provided, create a new thread
    if thread_id is None:
        thread_manager.create_thread()

    # Format the question with context and query the assistant
    formatted_question = (f"You will answer the following question with a summary, then provide a comprehensive answer, "
                          f"then provide the references aliasing them as Technical trace:\n\n{question}\n\nContext:\n{context}")
    messages, thread_id = thread_manager.add_message_and_wait_for_reply(formatted_question, [])
    return messages, thread_id

if __name__ == "__main__":
    # First query - introduce a piece of information
    initial_question = "My name is Roland, what do you know about my name?"
    initial_response, thread_id = query_assistant_with_context(initial_question, [])

    print("Initial Response:", initial_response)
    print("Thread ID from Initial Query:", thread_id)

    # Second query - follow-up question using the thread ID from the first query
    follow_up_question = "What was my name?"
    follow_up_response, _ = query_assistant_with_context(follow_up_question, [], thread_id=thread_id)

    print("Follow-up Response:", follow_up_response)
