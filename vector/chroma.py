import sqlite3
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from credentials import oai_api_key
from configuration import sql_file_path, vector_folder_path
from datetime import datetime


def get_data_from_db():
    # Connect to the SQLite database
    conn = sqlite3.connect(sql_file_path)
    cursor = conn.cursor()

    # Retrieve records from the "page_data" table where "lastUpdated" is newer than "last_embedded"
    cursor.execute("SELECT * FROM page_data WHERE lastUpdated > last_embedded OR last_embedded IS NULL")
    records = cursor.fetchall()

    # Process each record into a string
    all_documents = []
    page_ids = []
    for record in records:
        document = (
            f"Page id: {record[1]}, space key: {record[2]}, title: {record[3]}, "
            f"author: {record[4]}, created date: {record[5]}, last updated: {record[6]}, "
            f"content: {record[7]}, comments: {record[8]}"
        )
        all_documents.append(document)
        page_ids.append(record[1])

    # Close the SQLite connection
    conn.close()
    return all_documents, page_ids


def vectorize_documents(all_documents, page_ids):
    # Initialize OpenAI embeddings with the API key
    embedding = OpenAIEmbeddings(openai_api_key=oai_api_key)

    # Create the Chroma vectorstore with the embedding function
    vectordb = Chroma(embedding_function=embedding, persist_directory=vector_folder_path)

    # Prepare page_ids to be added as metadata
    metadatas = [{"page_id": page_id} for page_id in page_ids]

    # Add texts to the vectorstore
    vectordb.add_texts(texts=all_documents, metadatas=metadatas)

    # Persist the database
    vectordb.persist()

    # Update the last_embedded timestamp in the database
    conn = sqlite3.connect(sql_file_path)
    cursor = conn.cursor()
    current_time = datetime.now()
    for page_id in page_ids:
        cursor.execute("UPDATE page_data SET last_embedded = ? WHERE page_id = ?", (current_time, page_id))
    conn.commit()
    conn.close()


def add_to_vector():
    all_documents, page_ids = get_data_from_db()

    # Check if the lists are empty
    if not all_documents or not page_ids:
        print("No new or updated documents to vectorize.")
        return []

    vectorize_documents(all_documents, page_ids)
    print(f'Vectorized {len(all_documents)} documents.')
    print(f'Vectorized page ids: {page_ids}')
    return page_ids


def retrieve_relevant_documents(question):
    # Initialize OpenAI embeddings with the API key
    embedding = OpenAIEmbeddings(openai_api_key=oai_api_key)

    # Create the Chroma vectorstore with the embedding function
    vectordb = Chroma(embedding_function=embedding, persist_directory=vector_folder_path)

    # Embed the query text using the embedding function
    query_embedding = embedding.embed_query(question)

    # Perform a similarity search in the vectorstore
    similar_documents = vectordb.similarity_search_by_vector(query_embedding)

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
    vectorized_page_ids = add_to_vector()
    question = "do we use any reminder functionality in our solution?"
    relevant_document_ids = retrieve_relevant_documents(question)
    for result in relevant_document_ids:
        print(result)
        print("---------------------------------------------------")
