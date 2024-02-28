import logging
# some methods that could need change for this use case or be duplicated
from vector.chroma_threads import generate_embedding
from database.page_manager import add_or_update_embed_vector
from database.interaction_manager import QAInteractions


def format_interaction(interaction_id):
    """
    Format an interaction for vectorization.
    :param interaction_id: The ID of the interaction to format.
    :return: None
    """
    pass


def vectorize_interaction(interaction_id):
    """
    Vectorize an interaction.
    :param interaction_id: The ID of the interaction to vectorize.
    :return: None
    """
    pass


def store_interaction_in_db(interaction_id):
    """
    Store an interaction in the database.
    :param interaction_id: The ID of the interaction to store.
    :return: None
    """
    pass


def vectorize_interaction_and_store_in_db(interaction_id):
    """
    Vectorize an interaction and store it in the database.
    :param interaction_id: The ID of the interaction to vectorize.
    :return: None
    """
    format_interaction(interaction_id)
    vectorize_interaction(interaction_id)
    store_interaction_in_db(interaction_id)
    # logging.info(f"Interaction with ID {interaction_id} vectorized and stored in the database.")
    return None

