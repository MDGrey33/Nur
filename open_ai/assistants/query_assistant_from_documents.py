# ./oai_assistants/query_assistant_from_documents.py
from open_ai.assistants.utility import initiate_client
from open_ai.assistants.file_manager import FileManager
from open_ai.assistants.thread_manager import ThreadManager
from open_ai.assistants.assistant_manager import AssistantManager
from configuration import qa_assistant_id, file_system_path, MAX_CONTEXT_LENGTH
import logging

logging.basicConfig(level=logging.INFO)


def add_files_to_assistant(assistant, file_paths):
    """
    Adds specified files to a vector store and associates it with the assistant for retrieval in v2 API.

    Args:
    assistant (Assistant): The assistant to which files will be associated via vector store.
    file_paths (list of str): List of file paths to be uploaded and added to the vector store.
    """
    client = initiate_client()

    # Upload files and collect their IDs
    uploaded_file_ids = []
    for file_path in file_paths:
        file_obj = client.files.create(file=open(file_path, "rb"), purpose="assistants")
        uploaded_file_ids.append(file_obj.id)
        print(f"File uploaded successfully with ID: {file_obj.id}")

    # Create a vector store
    vector_store = client.beta.vector_stores.create()
    print(f"Vector store created with ID: {vector_store.id}")

    # Add files to the vector store
    for file_id in uploaded_file_ids:
        client.beta.vector_stores.files.create(vector_store_id=vector_store.id, file_id=file_id)
        print(f"File {file_id} added to vector store {vector_store.id}")

    # Update the assistant to use the vector store and retrieval tool
    updated_assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tools=[{"type": "retrieval"}],
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
    )
    print(f"Assistant {assistant.id} updated to use vector store {vector_store.id} with retrieval tool.")
    return updated_assistant


def format_pages_as_context(file_ids, max_length=MAX_CONTEXT_LENGTH):
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
        with open(chosen_file_path, "r") as file:
            file_content = file.read()
            # Check if adding the next file's content will exceed the max length
            title = file_content.split("title: ")[1].split("\n")[0].strip()
            space_key = file_content.split("spaceKey: ")[1].split("\n")[0].strip()
            additional_context = (
                f"\nDocument Title: {title}\nSpace Key: {space_key}\n\n{file_content}"
            )

            if len(context) + len(additional_context) <= max_length:
                context += additional_context
            else:
                # If adding the whole document would exceed the limit,
                # only add as much as possible, then break
                available_space = (
                    max_length
                    - len(context)
                    - len(" [Content truncated due to size limit.]")
                )
                context += (
                    additional_context[:available_space]
                    + " [Content truncated due to size limit.]"
                )
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
    assistant = assistant_manager.load_assistant(assistant_id=qa_assistant_id)
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
    formatted_question = (
        f"Here is the question and the context\n\n"
        f"{question}\n\n"
        f"Context:\n{context}"
    )
    print(f"Formatted question: {formatted_question}\n")

    # Query the assistant
    messages, thread_id = thread_manager.add_message_and_wait_for_reply(
        formatted_question, []
    )
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
    initial_question = "My name is Roland, what do you know about my name?"
    initial_response, thread_id = query_assistant_with_context(initial_question, [])

    print("Initial Response:", initial_response)
    print("Thread ID from Initial Query:", thread_id)

    # Second query - follow-up question using the thread ID from the first query
    follow_up_question = "What was my name?"
    follow_up_response, _ = query_assistant_with_context(
        follow_up_question, [], thread_id=thread_id
    )

    print("Follow-up Response:", follow_up_response)
