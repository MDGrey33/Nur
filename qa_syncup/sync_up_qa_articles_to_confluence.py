from confluence_integration.confluence_client import ConfluenceClient
from database.nur_database import QAInteractionManager, Session
import json


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


def get_qna_interactions_from_database():
    """
    Fetch all Q&A interactions from the database.

    Returns:
    list: A list of QAInteraction objects.
    """
    # Create a session instance
    session = Session()

    # Initialize QAInteractionManager with the session
    qa_manager = QAInteractionManager(session)

    # Fetch all Q&A interactions from the database
    all_interactions = qa_manager.get_qa_interactions()
    return all_interactions


def create_page_title_and_content(interaction):
    """
    Create the page title and content for a given interaction.

    Args:
    interaction (QAInteraction): A QAInteraction object.

    Returns:
    tuple: A tuple containing the page title and content.
    """
    # Create the page title and content
    title = interaction.question_text[:200]  # Use first 200 chars of the question as title
    comments = format_comment(interaction.comments)
    content = f"""
        <h2>Question</h2>
        <p>{interaction.question_text}</p>
        <h2>Answer</h2>
        <p>{interaction.answer_text}</p>
        <h2>Comments</h2>
        <p>{comments}</p>
        """

    return title, content


def create_page_on_confluence(confluence_client, interaction, space_key, title, content):
    """
    Create a page on Confluence.

    Args:
    space_key (str): The key of the Confluence space.
    title (str): The title of the page.
    clean_content (str): The content of the page.
    """
    clean_content = confluence_client.validate_and_coerce_xhtml(content)  # Validate and clean the content
    clean_title = confluence_client.validate_and_coerce_xhtml(title)
    # Check if a page with the same title already exists under the same space key
    if confluence_client.page_exists(space_key, clean_title):
        page_id = confluence_client.get_page_id_by_title(space_key, clean_title)
        if page_id:
            # Update the existing page if it's under the same space key
            confluence_client.update_page(page_id, clean_title, clean_content)
            return f"Page updated for interaction ID: {interaction.interaction_id}"
        else:
            # Skip if it's under a different space key
            return f"Skipping update for interaction ID: {interaction.interaction_id} - Page found under a different space key"
    else:
        # Create the page if it doesn't exist
        confluence_client.create_page(space_key, clean_title, clean_content)
        return f"Page created for interaction ID: {interaction.interaction_id}"


def sync_up_interactions_to_confluence():
    """
    Sync up all Q&A interactions to Confluence.
    """
    # Create a Confluence client instance
    confluence_client = ConfluenceClient()

    space_key = confluence_client.create_space_if_not_found("Nur documentation QnA")
    print(f"Space key: {space_key}")
    all_interactions = get_qna_interactions_from_database()

    # Iterate through each interaction
    for interaction in all_interactions:
        title, content = create_page_title_and_content(interaction)
        print(create_page_on_confluence(confluence_client, interaction, space_key, title, content))


if __name__ == "__main__":
    sync_up_interactions_to_confluence()