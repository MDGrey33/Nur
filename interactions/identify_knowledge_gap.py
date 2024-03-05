# ./interactions/identify_knowledge_gap.py
from typing import List
import chromadb
import logging
import json
from configuration import interactions_folder_path, embedding_model_id
from configuration import interaction_retrieval_count, interactions_collection_name
from configuration import quizz_assistant_id
from open_ai.embedding.embed_manager import embed_text
from oai_assistants.utility import initiate_client
from oai_assistants.thread_manager import ThreadManager
from oai_assistants.assistant_manager import AssistantManager
from database.interaction_manager import QAInteractionManager, QAInteractions

logging.basicConfig(level=logging.INFO)


def retrieve_relevant_interaction_ids(query: str) -> List[str]:
    """
    Retrieve the most relevant interactions for a given query using ChromaDB.

    Args:
        query (str): The query to retrieve relevant interactions for.

    Returns:
        List[str]: A list of interaction IDs of the most relevant interactions.
    """

    # Generate the query embedding using OpenAI
    try:
        query_embedding = embed_text(text=query, model=embedding_model_id)
    except Exception as e:
        logging.error(f"Error generating query embedding: {e}")
        return []

    # Initialize the ChromaDB client
    client = chromadb.PersistentClient(path=interactions_folder_path)

    collections = client.list_collections()
    logging.info(f"Available collections: {collections}")

    collection = client.get_collection(interactions_collection_name)

    # Perform a similarity search in the collection
    similar_items = collection.query(
        query_embeddings=[query_embedding],
        n_results=interaction_retrieval_count
    )

    # Extract and return the interaction IDs from the results
    if 'ids' in similar_items:
        interaction_ids = [id for sublist in similar_items['ids'] for id in sublist]
    else:
        logging.warning("No 'ids' key found in similar_items, no interactions retrieved.")
        interaction_ids = []

    return interaction_ids


def format_interactions(interactions: List[QAInteractions]) -> str:
    formatted_interactions = []
    for interaction in interactions:
        # Extract attributes
        question = f"Question: {interaction.question_text}"
        answer = f"Answer: {interaction.answer_text}"

        # Determine whether comments is a string (JSON) or already a list
        if isinstance(interaction.comments, str):
            try:
                comments = json.loads(interaction.comments)
            except json.JSONDecodeError:
                comments = []  # Default to an empty list if deserialization fails
        else:
            comments = interaction.comments  # Assume it's already a list if not a string

        # Format comments, handling both empty lists and lists of dictionaries
        if comments:
            comments_formatted = "Comments: " + "; ".join([f"{c.get('text', 'No text')}" for c in comments])
        else:
            comments_formatted = "Comments: No comments"

        # Combine question, answer, and comments for this interaction
        formatted_interaction = f"{question}\n{answer}\n{comments_formatted}\n---\n"
        formatted_interactions.append(formatted_interaction)

    all_interactions = "\n".join(formatted_interactions)
    return all_interactions


def query_assistant_with_context(query, formatted_interactions, thread_id=None):
    """
    Queries the assistant with a specific question, after setting up the necessary context by adding relevant interactions.

    Args:
    question (str): The question to be asked.
    page_ids (list): A list of page IDs representing the files to be added to the assistant's context.
    thread_id (str, optional): The ID of an existing thread to continue the conversation. Default is None.

    Returns:
    list: A list of messages, including the assistant's response to the question.
    """

    # Initiate the client
    client = initiate_client()
    print(f"Client initiated: {client}\n")
    assistant_manager = AssistantManager(client)
    print(f"Assistant manager initiated: {assistant_manager}\n")

    # Retrieve the assistant instance
    assistant = assistant_manager.load_assistant(assistant_id=quizz_assistant_id)
    print(f"Assistant loaded: {assistant}\n")

    # Initialize ThreadManager with or without an existing thread_id
    thread_manager = ThreadManager(client, assistant.id, thread_id)
    print(f"Thread manager initiated: {thread_manager}\n")

    # If no thread_id was provided, create a new thread
    if thread_id is None:
        thread_manager.create_thread()
        print(f"Thread created: {thread_manager.thread_id}\n")
    else:
        print(f"Thread loaded with the following ID: {thread_id}\n")

    # Format the question with context and query the assistant

    formatted_question = ("After analyzing the provided context and interactions, identify the crucial questions that "
                          "remain unanswered or partially answered. These questions should reflect gaps in our current "
                          "knowledge or documentation. Compile these questions into a JSON array, following the specified "
                          "structure. Each entry should include the question itself and a brief explanation of its "
                          "relevance, aiming to elucidate why addressing this question is vital for filling the "
                          "identified knowledge gap."
                          f"Relevant domain: {query} "
                          f"Context:{formatted_interactions}\n")

    print(f"Formatted question: {formatted_question}\n")

    # Query the assistant
    messages, thread_id = thread_manager.add_message_and_wait_for_reply(formatted_question, [])
    print(f"The thread_id is: {thread_id}\n Messages received: {messages}\n")
    if messages and messages.data:
        assistant_response = messages.data[0].content[0].text.value
        print(f"Assistant full response: {assistant_response}\n")
    else:
        assistant_response = "No response received."
        print(f"No response received.\n")

    return assistant_response, thread_id



def identify_knowledge_gaps(context):
    query = f"no information in context: {context}"
    interaction_ids = retrieve_relevant_interaction_ids(query)
    qa_interaction_manager = QAInteractionManager()
    relevant_qa_interactions = qa_interaction_manager.get_interactions_by_interaction_ids(interaction_ids)
    formatted_interactions = format_interactions(relevant_qa_interactions)
    questions_json = query_assistant_with_context(query, formatted_interactions)
    # identify the authors of the most similar documents as domain experts
    # identify the users who asked the questions as the users who need the information
    # post questions to slack while tagging the domain experts and the users who need the information
    print(questions_json)
