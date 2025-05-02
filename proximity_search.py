from vector.chroma import retrieve_relevant_documents
from database.page_manager import get_page_data_by_ids

if __name__ == "__main__":
    question = "who is the CEO of the company?"
    print(f"Running proximity search for: {question}\n")
    doc_ids = retrieve_relevant_documents(question)
    print(f"Relevant document IDs: {doc_ids}\n")
    if doc_ids:
        docs, ids = get_page_data_by_ids(doc_ids)
        for i, (doc, doc_id) in enumerate(zip(docs, ids)):
            print(f"Result {i+1} (ID: {doc_id}):\n{doc}\n{'-'*40}")
    else:
        print("No relevant documents found.") 