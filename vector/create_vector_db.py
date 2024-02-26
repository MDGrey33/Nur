# chroma_module.py
from configuration import vector_folder_path
import chromadb
from database.page_manager import get_all_page_data_from_db
import json
from confluence_integration.extract_page_content_and_store_processor import embed_pages_missing_embeds
from configuration import vector_collection_name

# Initialize the Chroma PersistentClient for disk persistence
client = chromadb.PersistentClient(path=vector_folder_path)


def add_to_vector(collection_name, space_key=None):
    """
    Retrieves all page data from the database, uses the stored embeddings, and adds them to the vector store.

    Args:
        collection_name (str): The name of the collection to store embeddings.
        space_key (str): The key of the space to retrieve page data from. If None, retrieves data from all spaces.
    """
    # Retrieve all documents, their corresponding IDs, and embeddings
    page_ids, _, embeddings = get_all_page_data_from_db(space_key=space_key)

    # Deserialize the embeddings and filter out None values
    valid_embeddings = []
    valid_page_ids = []
    for i, embed in enumerate(embeddings):
        if embed is None:
            print(f"Skipping embedding at index {i}: Embed is None")
            continue

        try:
            # Deserialize the JSON string into a Python list
            deserialized_embed = json.loads(embed)
            valid_embeddings.append(deserialized_embed)
            valid_page_ids.append(page_ids[i])
        except (json.JSONDecodeError, TypeError) as e:
            # Handle the exception if JSON deserialization fails
            print(f"Failed to deserialize embedding at index {i}: {e}")
            continue

        # Print progress update after every 10 embeddings for example
        if i % 10 == 0:
            print(f"Processed {i + 1}/{len(embeddings)} embeddings.")

    print("Completed deserializing all embeddings.")

    # Ensure the collection exists
    print(f"Ensuring collection '{collection_name}' exists...")
    collection = client.get_or_create_collection(collection_name)

    # Add embeddings to the collection
    print(f"Adding {len(valid_embeddings)} embeddings to the collection '{collection_name}'...")
    try:
        collection.upsert(
            ids=valid_page_ids,
            embeddings=valid_embeddings,
            metadatas=[{"page_id": pid} for pid in valid_page_ids]  # Assuming you want to store page IDs as metadata
        )
        print(f"Successfully added {len(valid_embeddings)} embeddings to the collection '{collection_name}'.")
    except Exception as e:
        print(f"Error adding embeddings to the collection: {e}")


def add_embeds_to_vector_db(space_key=None):
    """
    Adds the embeddings to the vector database.
    """
    collection_name = vector_collection_name
    add_to_vector(collection_name, space_key=space_key)
    print(f"Embeddings added to {collection_name} collection.")


if __name__ == '__main__':
    embed_pages_missing_embeds()
    add_embeds_to_vector_db()
    # initiate the collection and peek at the embeddings
    collection = client.get_collection(vector_collection_name)
    print(collection.peek())
    print(collection.count())
