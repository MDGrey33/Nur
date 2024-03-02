import logging
import time
import json
from database.interaction_manager import QAInteractionManager
from open_ai.embedding.embed_manager import embed_text
from configuration import embedding_model_id
from configuration import api_host, api_port
import requests
import os

host = os.environ.get("NUR_API_HOST", api_host)
port = os.environ.get("NUR_API_PORT", api_port)


def get_qna_interactions_from_database():
    """
    Fetch all Q&A interactions from the database.

    Returns:
    list: A list of QAInteraction objects.
    """

    # Initialize QAInteractionManager with the session
    qa_manager = QAInteractionManager()

    # Fetch all Q&A interactions from the database
    all_interactions = qa_manager.get_qa_interactions()
    return all_interactions


def get_qna_interactions_without_embeds():
    """
    Fetch all Q&A interactions from the database without embeds.

    Returns:
    list: A list of QAInteraction objects.
    """
    # Initialize QAInteractionManager with the session
    qa_manager = QAInteractionManager()

    # Fetch all Q&A interactions from the database
    all_interactions = qa_manager.get_interactions_without_embeds()
    return all_interactions


def format_comment(raw_comment):
    # Return an empty string or a default message if raw_comment is None
    if raw_comment is None:
        return "No comments available."

    # Proceed with the original processing
    try:
        comment_data = json.loads(raw_comment)
    except json.JSONDecodeError:
        # Handle cases where raw_comment is not a valid JSON string
        return "Invalid comment format."

    formatted_comments = []
    for comment in comment_data:
        text = comment["text"].replace('\n', ' ').strip()
        user = comment["user"]
        timestamp = comment["timestamp"]
        formatted_comments.append(f"{text} (Comment by {user} on {timestamp})")
    return ' '.join(formatted_comments)


def format_interaction(interaction):
    """
    Create a formatted string containing the page title and content for a given interaction.

    Args:
    interaction (QAInteraction): A QAInteraction object.

    Returns:
    str: A string containing the formatted page title and content.
    """
    # Create the page title and content
    comments = format_comment(interaction.comments)
    formatted_interaction = f"""
        <h2>Question</h2>
        <p>{interaction.question_text}</p>
        <h2>Answer</h2>
        <p>{interaction.answer_text}</p>
        <h2>Comments</h2>
        <p>{comments}</p>
        """
    return formatted_interaction


def vectorize_interaction(formatted_interaction, embedding_model_id):
    """
    Vectorize an interaction.
    :param formatted_interaction: The formatted interaction to vectorize.
    :param embedding_model_id: The ID of the embedding model to use.
    :return: The vectorized interaction.
    """
    embed = embed_text(formatted_interaction, embedding_model_id)
    return embed


def store_interaction_embed_in_db(interaction_id, embed_response_json):
    """
    Store an interaction's embedding in the database.
    :param interaction_id: The ID of the interaction to store.
    :param embed_response_json: The JSON string response containing the embedding.
    :return: None
    """
    interaction_manager = QAInteractionManager()
    # Directly use the JSON string of the embedding vector as received from embed_text
    interaction_manager.add_embed_to_interaction(interaction_id, embed_response_json)


def vectorize_interaction_and_store_in_db(interaction_id):
    interaction_manager = QAInteractionManager()
    interaction = interaction_manager.get_interaction_by_interaction_id(interaction_id)  # Assuming this method exists and correctly fetches the interaction
    if interaction:
        formatted_interaction = format_interaction(interaction)
        embed = vectorize_interaction(formatted_interaction, embedding_model_id)
        store_interaction_embed_in_db(interaction_id, embed)
        logging.info(f"Interaction with ID {interaction_id} vectorized and stored in the database.")
    else:
        logging.error(f"No interaction found for ID {interaction_id}")
    return None


# a function that submits an API request to create_interaction_embeds
def submit_create_interaction_embeds_request(interaction_id):
    """
    Submit an API request to create interaction embeds.
    :return: None
    """

    endpoint_url = f'http://{host}:{port}/api/v1/interaction_embeds'
    headers = {"Content-Type": "application/json"}
    # The key here should be "interaction_id" as expected by the InteractionEmbedRequest model in the FastAPI endpoint
    payload = {"interaction_id": interaction_id}

    try:
        response = requests.post(endpoint_url, json=payload, headers=headers)
        response.raise_for_status()  # This will raise for HTTP errors
        logging.info(f"Embedding creation request successful for interaction ID {interaction_id}.")
    except requests.exceptions.HTTPError as e:
        logging.error(
            f"HTTP error occurred while submitting embedding creation request for interaction ID {interaction_id}: {e}")
    except Exception as e:
        logging.error(
            f"An error occurred while submitting embedding creation request for interaction ID {interaction_id}: {e}")


def vectorize_interactions_and_store_in_db(retry_limit: int = 3, wait_time: int = 5) -> None:
    """
    Vectorize all interactions without embeds and store them in the database,
    with retries for failed attempts.
    """
    for attempt in range(retry_limit):
        # Retrieve interactions that are still missing embeddings.
        interactions = get_qna_interactions_without_embeds()

        # If there are no interactions missing embeddings, exit the loop and end the process.
        if not interactions:
            print("All interactions have embeddings. Process complete.")
            return

        print(
            f"Attempt {attempt + 1} of {retry_limit}: Processing {len(interactions)} interactions missing embeddings.")
        for interaction in interactions:
            try:
                # Attempt to vectorize and store each interaction.
                submit_create_interaction_embeds_request(str(interaction.interaction_id))
                # A brief delay between processing to manage load.
                time.sleep(0.5)
            except Exception as e:
                logging.error(f"An error occurred while vectorizing interaction with ID {interaction.interaction_id}: {e}")

        print(f"Waiting for {wait_time} seconds for embeddings to be processed...")
        time.sleep(wait_time)

        # After waiting, retrieve the list of interactions still missing embeddings to see if the list has decreased.
        interactions = get_qna_interactions_without_embeds()
        if not interactions:
            print("All interactions now have embeddings. Process complete.")
            break  # Break out of the loop if there are no more interactions missing embeddings.

        print(f"After attempt {attempt + 1}, {len(interactions)} interactions are still missing embeds.")

    # After exhausting the retry limit, check if there are still interactions without embeddings.
    if interactions:
        print("Some interactions still lack embeddings after all attempts.")
    else:
        print("All interactions now have embeddings. Process complete.")
        print("\n#\n#\n#\nembeds added to DB but creating a chromadb is not done yet\n#\n#\n#")


if __name__ == "__main__":
    vectorize_interactions_and_store_in_db()
