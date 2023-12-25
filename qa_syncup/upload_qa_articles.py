from atlassian import Confluence
from confluence_integration.confluence_client import ConfluenceClient
from credentials import confluence_credentials
from database.confluence_database import QAInteractionManager, Session

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

# Iterate through each interaction and create a Confluence page
for interaction in all_interactions:
    title = interaction.question_text[:50]  # Use first 50 chars of the question as title
    content = f"""
    <h2>Question</h2>
    <p>{interaction.question_text}</p>
    <h2>Answer</h2>
    <p>{interaction.answer_text}</p>
    <h2>Comments</h2>
    <p>{interaction.comments}</p>
    """
    # Create the page in Confluence
    confluence_client.create_page(space_key, title, content)
    print(f"Page created for interaction ID: {interaction.interaction_id}")
