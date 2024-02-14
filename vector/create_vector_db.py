# chroma_module.py
from configuration import vector_folder_path
import chromadb
from database.nur_database import get_all_page_data_from_db
import json
from confluence_integration.extract_page_content_and_store_processor import embed_pages_missing_embeds

# Initialize the Chroma PersistentClient for disk persistence
client = chromadb.PersistentClient(path=vector_folder_path)


def add_to_vector(collection_name):
    """
    Retrieves all page data from the database, uses the stored embeddings, and adds them to the vector store.

    Args:
        collection_name (str): The name of the collection to store embeddings.
    """
    # Retrieve all documents, their corresponding IDs, and embeddings
    page_ids, _, embeddings = get_all_page_data_from_db()

    embeddings_deserialized = []
    for i, embed in enumerate(embeddings):
        if embed is None:
            print(f"Skipping embedding at index {i}: Embed is None")
            embeddings_deserialized.append(None)
            continue

        try:
            # Deserialize the JSON string into a Python list
            deserialized_embed = json.loads(embed)
            embeddings_deserialized.append(deserialized_embed)
        except (json.JSONDecodeError, TypeError) as e:
            # Handle the exception if JSON deserialization fails
            print(f"Failed to deserialize embedding at index {i}: {e}")
            embeddings_deserialized.append(None)

        # Print progress update after every 10 embeddings for example
        if i % 10 == 0:
            print(f"Processed {i + 1}/{len(embeddings)} embeddings.")

    # At the end, you could print a final statement indicating completion
    print("Completed deserializing all embeddings.")
    # Create a map of page IDs to embeddings
    page_embed_map = dict(zip(page_ids, embeddings_deserialized))


def add_embeds_to_vector_db():
    # Specify your collection name here
    collection_name = "TopAssist"
    add_to_vector(collection_name)
    print(f"Embeddings added to {collection_name} collection.")


if __name__ == '__main__':
    embed_pages_missing_embeds()
    add_embeds_to_vector_db()
    # initiate the collection and peek at the embeddings
    collection = client.get_collection("TopAssist")
    print(collection.peek())
    print(collection.count())
