from configuration import vector_folder_path
import chromadb
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)


def rename_collection(client, old_name, new_name):
    """
    Uses the modify method to rename a collection in ChromaDB.
    """
    # Fetch the collection to be renamed
    collection = client.get_collection(old_name)
    # Rename the collection using the modify method
    collection.modify(name=new_name)
    logging.info(f"Collection '{old_name}' has been renamed to '{new_name}' successfully.")


if __name__ == '__main__':
    # Initialize the ChromaDB client
    client = chromadb.PersistentClient(path=vector_folder_path)

    # Define the old and new collection names
    old_collection_name = input("old collection name: ")
    new_collection_name = input("new collection name: ")

    # Attempt to rename the collection
    rename_collection(client, old_collection_name, new_collection_name)

    # Proceed with operations using the new collection name
    print(f"Operations will now proceed using the new collection name: {new_collection_name}")
