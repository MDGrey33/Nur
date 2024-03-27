# ./confluence_integration/system_knowledge_manager.py
# Used as part of knowledge gap recovery to create pages retrieved from quiz
# after knowledge gap recovery to store them on confluence
from configuration import system_confluence_knowledge_space
from confluence_integration.confluence_client import ConfluenceClient


def create_page_on_confluence(title, content):
    """
    Create a page on Confluence.

    Args:
    space_key (str): The key of the Confluence space.
    title (str): The title of the page.
    clean_content (str): The content of the page.
    """
    confluence_client = ConfluenceClient()
    space_key = confluence_client.create_space_if_not_found(system_confluence_knowledge_space)
    print(f"Space key: {space_key}")

    clean_content = confluence_client.validate_and_coerce_xhtml(content)  # Validate and clean the content
    clean_title = confluence_client.validate_and_coerce_xhtml(title)
    # Check if a page with the same title already exists under the same space key
    if confluence_client.page_exists(space_key, clean_title):
        page_id = confluence_client.get_page_id_by_title(space_key, clean_title)
        if page_id:
            # Update the existing page if it's under the same space key
            confluence_client.update_page(page_id, clean_title, clean_content)
        else:
            # Skip if it's under a different space key
            return f"Skipping update for interaction  - Page found under a different space key"
    else:
        # Create the page if it doesn't exist
        confluence_client.create_page(space_key, clean_title, clean_content)
        return f"Page created"
