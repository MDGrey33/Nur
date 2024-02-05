import json
from configuration import file_system_path
from vector.chroma_threads import retrieve_relevant_documents


def format_pages_as_context(file_ids, max_length=30000):
    """
    Formats specified files as a context string and additional details for referencing in responses,
    ensuring the total context length does not exceed the specified maximum length.

    Args:
        file_ids (list of str): List of file IDs to be formatted as context.
        max_length (int): The maximum length allowed for the context.

    Returns:
        list of dicts: Each dict contains the document title, space key, and content, truncated if necessary.
    """
    documents = []
    total_length = 0
    for file_id in file_ids:
        if total_length >= max_length:
            break
        chosen_file_path = file_system_path + f"/{file_id}.txt"
        with open(chosen_file_path, 'r') as file:
            file_content = file.read()
            title = file_content.split('title: ')[1].split('\n')[0].strip()
            space_key = file_content.split('spaceKey: ')[1].split('\n')[0].strip()
            document = {
                "id": file_id,
                "title": title,
                "spaceKey": space_key,
                "content": file_content
            }
            document_length = len(json.dumps(document))
            if total_length + document_length <= max_length:
                documents.append(document)
                total_length += document_length
            else:
                break  # Stop adding more content to ensure we respect the maximum length

    # Truncate the last document's content if total_length exceeds max_length
    if total_length > max_length:
        last_doc = documents[-1]
        available_space = max_length - (total_length - len(last_doc['content']))
        last_doc['content'] = last_doc['content'][:available_space] + " [Content truncated due to size limit.]"

    return documents


def get_context(context_query, max_length=10000):
    """
    Retrieves relevant documents based on a context query and formats them for use as context,
    with the entire response structured as a JSON-compatible dictionary.

    Args:
        context_query (str): The query to retrieve relevant context for.
        max_length (int): The maximum length allowed for the combined context.

    Returns:
        dict: A dictionary with 'document_ids' and 'documents', where 'documents' is a list of dicts
              containing the document title, space key, and content.
    """
    context_document_ids = retrieve_relevant_documents(context_query)
    documents = format_pages_as_context(context_document_ids, max_length)
    return {
        "document_ids": context_document_ids,
        "documents": documents
    }
