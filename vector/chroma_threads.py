# ./vector/chroma_threads.py
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from configuration import vector_folder_path, file_system_path, embedding_model_id
from database.page_manager import get_page_data_from_db
from database.page_manager import update_embed_date
from credentials import oai_api_key
from file_system.file_manager import FileManager
import chromadb
import logging
from typing import List
from configuration import document_count
from open_ai.embedding.embed_manager import embed_text


def generate_embedding(page_id, model=embedding_model_id):
    """
    Generates an embedding for the given text using the specified OpenAI model.
    Returns a tuple of (embedding, error_message).
    """
    file_manager = FileManager()
    try:
        page_content = file_manager.read(f"{file_system_path}/{page_id}.txt")
        # Ensure the content does not exceed the maximum token limit
        page_content = page_content[:8190]
    except Exception as e:
        logging.error(f"Error reading page content for page ID {page_id}: {e}")
        return None, f"Error reading page content: {e}"

    try:
        response = embed_text(text=page_content, model=model)
        # Extract the embedding correctly from the response object
        if response.data and len(response.data) > 0:
            embedding = response.data[0].embedding
            return embedding, None
        else:
            return None, "No embedding data returned for the page."
    except Exception as e:
        error_message = f"Error generating embedding for page ID {page_id}: {e}"
        logging.error(error_message)
        return None, error_message


def retrieve_relevant_documents(question: str) -> List[str]:
    """
    Retrieve the most relevant documents for a given question using ChromaDB.

    Args:
    question (str): The question to retrieve relevant documents for.

    Returns:
    List[str]: A list of document IDs of the most relevant documents.
    """

    # Generate the query embedding using OpenAI
    query_embedding = embed_text(text=question, model=embedding_model_id)

    # Initialize the ChromaDB client
    client = chromadb.PersistentClient(path=vector_folder_path)

    collections = client.list_collections()
    print(f"Available collections: {collections}")

    # Assuming you have a collection named 'documents' in your ChromaDB
    collection = client.get_collection('TopAssist')

    count_result = collection.count()

    print(f"\n{count_result} results\n")

    # Perform a similarity search in the collection
    similar_items = collection.query(
        query_embeddings=[query_embedding],
        n_results=document_count
    )

    # Extract and return the document IDs from the metadata of similar items
    #document_ids = [item['metadata']['page_id'] for item in similar_items['results'] if'metadata' in item and 'page_id' in item['metadata']]
    if 'ids' in similar_items:
        document_ids = [id for sublist in similar_items['ids'] for id in sublist]
    else:
        print("No 'ids' key found in similar_items")
        document_ids = []

    return document_ids


# might be unused candidate for removal
def vectorize_documents(all_documents, page_ids):
    """
    Vectorize a list of documents and add them to the vectorstore.
    :param all_documents:
    :param page_ids:
    :return: page ids of the vectorized documents
    """

    # Initialize OpenAI embeddings with the API key
    embedding = OpenAIEmbeddings(openai_api_key=oai_api_key, model=embedding_model_id)

    # Create the Chroma vectorstore with the embedding function
    vectordb = Chroma(embedding_function=embedding, persist_directory=vector_folder_path)

    # Prepare page_ids to be added as metadata
    metadatas = [{"page_id": page_id} for page_id in page_ids]

    # Add texts to the vectorstore
    vectordb.add_texts(texts=all_documents, metadatas=metadatas)

    # Persist the database
    vectordb.persist()

    # Update the last_embedded timestamp in the database
    update_embed_date(page_ids)

    # Return the page ids of the vectorized documents
    return page_ids


# might be unused candidate for removal
def add_to_vector():
    """
    Vectorize all new or updated documents and add them to the vectorstore.
    :return: page ids
    """
    all_documents, page_ids = get_page_data_from_db()

    # Check if the lists are empty
    if not all_documents or not page_ids:
        print("No new or updated documents to vectorize.")
        return []

    vectorize_documents(all_documents, page_ids)
    print(f'Vectorized {len(all_documents)} documents.')
    print(f'Vectorized page ids: {page_ids}')
    return page_ids




# might be unused candidate for removal
def retrieve_relevant_documents_langchain(question):
    """
    Retrieve the most relevant documents for a given question.
    :param question:
    :return: document ids
    """
    # Initialize OpenAI embeddings with the API key
    embedding = OpenAIEmbeddings(openai_api_key=oai_api_key, model=embedding_model_id)

    # Create the Chroma vectorstore with the embedding function
    vectordb = Chroma(embedding_function=embedding, persist_directory=vector_folder_path)

    # Embed the query text using the embedding function
    query_embedding = embedding.embed_query(question)

    # Perform a similarity search in the vectorstore
    similar_documents = vectordb.similarity_search_by_vector(query_embedding, k=document_count)

    # Process and return the results along with their metadata
    results = []
    for doc in similar_documents:
        result = {
            "page_content": doc.page_content,
            "metadata": doc.metadata
        }
        results.append(result)
    document_ids = [doc.metadata.get('page_id') for doc in similar_documents if doc.metadata]

    return document_ids


if __name__ == '__main__':
    # Call the function with a test page ID and print the outcome
    page_id = 420577502  # Example page ID for debugging
    embedding, error = generate_embedding(page_id)
    print("Embedding:", embedding)
    print("Error:", error)