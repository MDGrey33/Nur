import chromadb
from configuration import vector_folder_path, pages_collection_name

PAGE_ID = "81796825385"

if __name__ == "__main__":
    client = chromadb.PersistentClient(path=vector_folder_path)
    collection = client.get_collection(pages_collection_name)
    print(f"Looking up page_id={PAGE_ID} in Chroma collection '{pages_collection_name}'...")
    # Try with 'page_id' key
    result = collection.get(where={"page_id": PAGE_ID})
    if result["ids"]:
        print(f"Found with 'page_id': {result}")
    else:
        # Try with 'id' key
        result = collection.get(where={"id": PAGE_ID})
        if result["ids"]:
            print(f"Found with 'id': {result}")
        else:
            print("Page ID not found in Chroma metadata.") 