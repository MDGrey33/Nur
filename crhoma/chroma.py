import sqlite3
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from credentials import oai_api_key


def get_data_from_db():
    # Connect to the SQLite database
    conn = sqlite3.connect('../database/confluence_data.db')
    cursor = conn.cursor()

    # Retrieve all records from the "page_data" table
    cursor.execute("SELECT * FROM page_data")
    records = cursor.fetchall()

    # Process each record into a string
    all_documents = [
        f"Page id: {record[1]}, space key: {record[2]}, title: {record[3]}, "
        f"author: {record[4]}, created date: {record[5]}, last updated: {record[6]}, "
        f"content: {record[7]}, comments: {record[8]}"
        for record in records
    ]

    # Close the SQLite connection
    conn.close()
    return all_documents


def vectorize_documents(all_documents):

    # Initialize OpenAI embeddings with the API key
    embedding = OpenAIEmbeddings(openai_api_key=oai_api_key)

    # Create the Chroma vectorstore with the embedding function
    vectordb = Chroma(embedding_function=embedding, persist_directory='db')

    # Add texts to the vectorstore
    vectordb.add_texts(texts=all_documents)

    # Persist the database
    vectordb.persist()


def add():
    all_documents = get_data_from_db()
    vectorize_documents(all_documents)


def retrieve(question):
    # Initialize OpenAI embeddings with the API key
    embedding = OpenAIEmbeddings(openai_api_key=oai_api_key)

    # Create the Chroma vectorstore with the embedding function
    vectordb = Chroma(embedding_function=embedding, persist_directory='db')

    # Embed the query text using the embedding function
    query_embedding = embedding.embed_query(question)

    # Perform a similarity search in the vectorstore
    similar_documents = vectordb.similarity_search_by_vector(query_embedding)

    # Process and return the results
    return [doc.page_content for doc in similar_documents]


if __name__ == '__main__':
    add()
    question = "do we use any reminder functionality in our solution?"
    results = retrieve(question)
    for doc in results:
        print(doc)



