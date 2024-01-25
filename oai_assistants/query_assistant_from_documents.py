# ./oai_assistants/query_assistant_from_documents.py
from oai_assistants.utility import initiate_client
from oai_assistants.file_manager import FileManager
from oai_assistants.thread_manager import ThreadManager
from oai_assistants.assistant_manager import AssistantManager
from configuration import assistant_id


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
        chosen_file_path = f"/Users/roland/code/Nur/content/file_system/{file_id}.txt"
        purpose = "assistants"
        uploaded_file_id = file_manager.create(chosen_file_path, purpose)
        print(f"File uploaded successfully with ID: {uploaded_file_id}")

        assistant_manager.add_file_to_assistant(assistant.id, uploaded_file_id)
        print(f"File {chosen_file_path} added to assistant {assistant.id}")


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

    # Add relevant files to the assistant
    add_files_to_assistant(assistant, page_ids)

    # Initialize ThreadManager with or without an existing thread_id
    thread_manager = ThreadManager(client, assistant.id, thread_id)

    # If no thread_id was provided, create a new thread
    if thread_id is None:
        thread_manager.create_thread()

    # Format the question and query the assistant
    formatted_question = (f"You will answer the following question with a summary, then provide a comprehensive answer, "
                          f"then provide the references aliasing them as Technical trace: {question}")
    messages, thread_id = thread_manager.add_message_and_wait_for_reply(formatted_question, [])
    return messages, thread_id


if __name__ == "__main__":
    query_assistant_with_context("Do we support payment matching in our solution? and if the payment is not matched "
                                 "do we already have a way to notify the client that they have a delayed payment?",
                                 [])
