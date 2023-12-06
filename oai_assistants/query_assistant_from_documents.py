# ./oai_assistants/query_assistant_from_documents.py
from oai_assistants.openai_assistant import create_assistant
from oai_assistants.utility import initiate_client
from oai_assistants.file_manager import FileManager
from oai_assistants.thread_manager import ThreadManager
from oai_assistants.assistant_manager import AssistantManager


def create_new_assistant():
    """
    Creates a new assistant with the specified parameters.
    """
    client = initiate_client()

    new_assistant = {
        "model": "gpt-4-1106-preview",
        "name": "Shams",
        "instructions": """You are the Q&A Assistant, 
        you know everything about the uploaded files
        and you review them and answer primarily from their content
        if you ever answer from outside the files, you will be penalized
        if you use your knowledge to explain some information from outside the file, you will clearly state that.
        """,
        "tools": [{"type": "code_interpreter"}, {"type": "retrieval"}],
        "description": "The ultimate librarian",
        "file_ids": []
    }

    assistant = create_assistant(client, new_assistant)
    print(assistant)
    return assistant


def add_files_to_assistant(assistant, file_ids):
    """
    Adds multiple files to an assistant's list of files.
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


def ask_assistant(assistant, question):
    """
    Asks an assistant a question.
    """
    client = initiate_client()
    thread_manager = ThreadManager(client, assistant.id)
    thread_manager.create_thread()
    question = (f"You will answer the following question with a summary, then provide a comprehensive answer, "
                f"then provide the references aliasing them as Technical trace: {question}")
    messages = thread_manager.add_message_and_wait_for_reply(question, [])
    return messages


def get_response_from_assistant(question, page_ids):
    assistant = create_new_assistant()

    if not isinstance(page_ids, list):
        page_ids = [page_ids]

    add_files_to_assistant(assistant, page_ids)
    messages = ask_assistant(assistant, question)
    # print(messages)
    return messages


if __name__ == "__main__":
    get_response_from_assistant("Do we support payment matching in our solution? and if the payment is not matched do we already have a way to notify the client that they have a delayed payment?", ["458841", "491570"])
