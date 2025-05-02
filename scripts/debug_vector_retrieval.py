from vector.chroma import retrieve_relevant_documents
from open_ai.embedding.embed_manager import embed_text
from configuration import embedding_model_id, pages_collection_name, vector_folder_path
import chromadb


def debug_vector_retrieval(query, n_results=5):
    # Step 1: Embed the query
    query_embedding = embed_text(text=query, model=embedding_model_id)

    # Step 2: Connect to ChromaDB
    client = chromadb.PersistentClient(path=vector_folder_path)
    collection = client.get_collection(pages_collection_name)

    # Step 3: Query the collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["metadatas", "distances", "documents"]
    )

    # Step 4: Print results
    print(f"Top {n_results} results for query: '{query}'")
    for i, (doc_id, distance, metadata) in enumerate(zip(results['ids'][0], results['distances'][0], results['metadatas'][0])):
        title = metadata.get('title', '[No Title]') if metadata else '[No Metadata]'
        print(f"{i+1}. ID: {doc_id}, Score: {distance}, Title: {title}, Metadata: {metadata}")


def check_document_exists(page_id):
    client = chromadb.PersistentClient(path=vector_folder_path)
    collection = client.get_collection(pages_collection_name)
    # Try to get the document by id
    results = collection.get(ids=[page_id], include=["metadatas", "documents"])
    if results['ids']:
        print(f"Document with page_id {page_id} exists in vector DB.")
        print(f"Metadata: {results['metadatas'][0]}")
        print(f"Document: {results['documents'][0]}")
    else:
        print(f"Document with page_id {page_id} does NOT exist in vector DB.")

if __name__ == "__main__":
    debug_vector_retrieval("who is the ceo of the company", n_results=5)
    check_document_exists("81809342499") 