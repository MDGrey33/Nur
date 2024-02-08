# ./oai_assistants/utility.py
from openai import OpenAI
from credentials import oai_api_key
import os
from configuration import model_id



def initiate_client():
    """
    Initializes and returns an OpenAI client using the provided API key.

    Returns:
    OpenAI: An instance of the OpenAI client configured with the specified API key.
    """
    client = OpenAI(api_key=oai_api_key)
    return client


def get_all_files_in_path(file_path):
    """
    Returns a list of all file paths within the specified directory and its subdirectories.
    Skips '.DS_Store' files common on macOS.

    Args:
    - directory (str): The path to the directory.

    Returns:
    - list: A list of file paths.
    """
    all_file_paths = []
    for root, _, files in os.walk(file_path):
        for file in files:
            if file != '.DS_Store':
                all_file_paths.append(os.path.join(root, file))
    return all_file_paths


# Additional function to select a file for upload
def select_file_for_upload(file_path):
    """
    Presents a list of all files in the specified path and allows the user to select a file for upload.

    Parameters:
    file_path (str): The path where files are located.

    Returns:
    str: The path of the selected file, or None if the selection is invalid.
    """
    all_files = get_all_files_in_path(file_path)
    print("Please select a file to upload:")
    for idx, file_name in enumerate(all_files):
        print(f"{idx + 1}. {file_name}")
    selected_index = int(input("Enter the number of the file you want to upload: ")) - 1
    if 0 <= selected_index < len(all_files):
        return all_files[selected_index]
    else:
        print("Invalid selection.")
        return None


# Sample assistant template used for creating new assistants in the system.
new_assistant = {
    "model": model_id,
    "name": "Shams",
    "instructions": """Your role is to serve as a Q&A-based knowledge base assistant.
Prioritize reviewing and referencing the documents provided as context or conversation history.
Generate responses exclusively from the information available in the provided context documents previous context documents and conversation history or context you retrieved using the context retrieval tool.
You can use the retrieval tool multiple times with different queries to satisfy the question.
Refrain from improvisation or sourcing content from other sources.
Utilize logical reasoning and deduction based on the conversation history and previous context.
If you lack an answer from the files and you attempted context retrieval without success, clearly state it and abstain from responding.
Disclose when using external knowledge to explain information beyond the provided files.
Format your responses as follows:  
summary: [providing a short to the point answer]
comprehensive answer: [providing a detailed answer]
technical trace: [providing the source of the information]""",
    "description": "The Ultimate Documentation AI",
    "file_ids": [],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_context",
                "description": "Retrieve relevant documents based on a context query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "context_query": {
                            "type": "string",
                            "description": "The query to retrieve relevant context for"
                        },
                        "max_length": {
                            "type": "integer",
                            "description": "The maximum length of the returned context"
                        }
                    },
                    "required": [
                        "context_query"
                    ]
                }
            }
        }
    ]
}