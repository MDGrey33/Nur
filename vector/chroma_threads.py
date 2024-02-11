# ./vector/chroma_threads.py
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from credentials import oai_api_key
from configuration import vector_folder_path, embedding_model_id
from database.nur_database import get_page_data_from_db
from database.nur_database import update_embed_date
import openai
from credentials import oai_api_key
from database.nur_database import add_or_update_embed_vector


client = openai.OpenAI(api_key=oai_api_key)


def generate_embedding(text, model="text-embedding-ada-002"):
    """
    Generates an embedding for the given text using the specified OpenAI model.

    Args:
        text (str): The text to embed.
        model (str): The model to use for embedding. Defaults to "text-embedding-ada-002".

    Returns:
        list: The embedding vector as a list of floats.
    """
    try:
        response = client.embeddings.create(input=text, model=model)
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []



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


def retrieve_relevant_documents(question):
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
    similar_documents = vectordb.similarity_search_by_vector(query_embedding, k=15)

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
    '''
    # Example usage
    text = "This is an example text to generate an embedding."
    embedding = generate_embedding(text)
    print(embedding)
    '''
    '''
    # vectorized_page_ids = add_to_vector()
    question = "what is the functionality of this solution?"
    relevant_document_ids = retrieve_relevant_documents(question)
    for result in relevant_document_ids:
        print(result)
        print("---------------------------------------------------")
    '''
    pass
