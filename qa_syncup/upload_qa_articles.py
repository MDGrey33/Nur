from atlassian import Confluence
from confluence_integration.confluence_client import ConfluenceClient
from credentials import confluence_credentials
from database.confluence_database import QAInteractionManager, Session
from bs4 import BeautifulSoup
import json


def format_comment(raw_comment):
    comment_data = json.loads(raw_comment)
    formatted_comments = []
    for comment in comment_data:
        text = comment["text"].replace('\n', ' ').strip()
        user = comment["user"]
        timestamp = comment["timestamp"]
        formatted_comments.append(f"{text} (Comment by {user} on {timestamp})")
    return ' '.join(formatted_comments)


# Initialize Confluence API
confluence = Confluence(
    url=confluence_credentials['base_url'],
    username=confluence_credentials['username'],
    password=confluence_credentials['api_token']
)

# Create a session instance
session = Session()

# Initialize ConfluenceClient and QAInteractionManager with the session
confluence_client = ConfluenceClient()
qa_manager = QAInteractionManager(session)

# Ensure the space exists and get its key
space_name = "Nur documentation QnA"
space_key = confluence_client.create_space_if_not_found(space_name)
print(space_key)

# Fetch all Q&A interactions from the database
all_interactions = qa_manager.get_qa_interactions()

# Iterate through each interaction
for interaction in all_interactions:
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

    # Clean and convert to a string using BeautifulSoup
    clean_content = BeautifulSoup(content, "html.parser").prettify()

    # Check if a page with the same title already exists under the same space key
    if confluence_client.page_exists(space_key, title):
        page_id = confluence_client.get_page_id_by_title(space_key, title)
        if page_id:
            # Update the existing page if it's under the same space key
            confluence_client.update_page(page_id, title, clean_content)
            print(f"Page updated for interaction ID: {interaction.interaction_id}")
        else:
            # Skip if it's under a different space key
            print(f"Skipping update for interaction ID: {interaction.interaction_id} - Page found under a different space key")
    else:
        # Create the page if it doesn't exist
        confluence_client.create_page(space_key, title, clean_content)
        print(f"Page created for interaction ID: {interaction.interaction_id}")
