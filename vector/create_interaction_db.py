import json

from configuration import interactions_collection_name
from database.interaction_manager import QAInteractionManager
import chromadb
from configuration import interactions_folder_path


class VectorInteractionManager:

    def __init__(self):
        self.client = chromadb.PersistentClient(path=interactions_folder_path)

    def add_to_vector(self):
        collection_name = interactions_collection_name

        # Get interactions with embedings
        qa_interaction_manager = QAInteractionManager()
        interactions = qa_interaction_manager.get_interactions_with_embeds()

        interaction_ids = []
        interaction_embeddings = []
        for interaction in interactions:
            interaction_ids.append(str(interaction.interaction_id))
            interaction_embeddings.append(json.loads(interaction.embed))

        # Ensure the collection exists
        print(f"Ensuring collection '{collection_name}' exists...")
        collection = self.client.get_or_create_collection(collection_name)

        # Add interactions to the collection
        print(
            f"Adding {len(interactions)} interactions to the collection '{collection_name}'..."
        )
        try:
            collection.upsert(
                ids=interaction_ids,
                embeddings=interaction_embeddings,
                metadatas=[{"interaction_id": iid} for iid in interaction_ids],
                # Assuming you want to store page IDs as metadata
            )
            print(
                f"Successfully added {len(interaction_embeddings)} interactions to the collection '{collection_name}'."
            )

            print(f"collection count {collection.count()} ")

        except Exception as e:
            print(f"Error adding interactions to the collection: {e}")
