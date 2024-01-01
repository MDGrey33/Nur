from atlassian import Confluence
from credentials import confluence_credentials
import logging
import time
from bs4 import BeautifulSoup
import re

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



class ConfluenceClient:
    """
    A class to handle interactions with the Confluence API.
    """

    def __init__(self):
        """
        Initialize the Confluence client.

        Args:
        url (str): The base URL of the Confluence instance.
        username (str): The username for authentication.
        api_token (str): The API token for authentication.
        """
        self.initialize_confluence_client()


    def initialize_confluence_client(self):
        """
        Initialize the Confluence client.
        """
        self.confluence = Confluence(
            url=confluence_credentials['base_url'],
            username=confluence_credentials['username'],
            password=confluence_credentials['api_token']
        )

    def page_exists(self, space_key, title):
        """Check if a page with the given title exists in the given space."""
        return self.confluence.page_exists(space_key, title)

    def get_page_id_by_title(self, space_key, title):
        """Retrieve the page ID for a given page title in a given space."""
        try:
            return self.confluence.get_page_id(space_key, title)
        except Exception as e:
            print(f"Error retrieving page ID for {title}: {e}")
            return None

    def validate_and_coerce_xhtml(self, content):
        """
        Validates and coerces content to be XHTML compliant.
        Cleans special characters and converts Slack user mentions and URLs.

        Args:
            content (str): The HTML content to validate and clean.

        Returns:
            str: XHTML compliant content.
        """
        try:
            # Parse content using BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')

            # Convert Slack user mentions (<@U024UF2F68H>) to a readable format
            for user_mention in soup.find_all(text=re.compile("<@[A-Z0-9]+>")):
                readable_mention = re.sub(r"<@([A-Z0-9]+)>", r"User[\1]", user_mention)
                user_mention.replace_with(readable_mention)

            # Convert Slack URLs to standard anchor tags
            for link in soup.find_all(text=re.compile("<https?://[^\s]+>")):
                url = re.search(r"<(https?://[^\s]+)>", link)
                if url:
                    new_link = soup.new_tag("a", href=url.group(1))
                    new_link.string = url.group(1)
                    link.replace_with(new_link)

            # Escape special characters
            clean_content = str(soup).replace("<", "&lt;").replace(">", "&gt;")

            # Further clean the content if necessary, e.g., removing or replacing other special characters

            return clean_content
        except Exception as e:
            logging.error("Error validating/coercing content to XHTML: %s", e, exc_info=True)
            # Handle the error as per your policy, e.g., re-raise, return None, or provide default content
            raise

    def update_page(self, page_id, title, content):
        """Update an existing page with new content."""
        clean_content = self.validate_and_coerce_xhtml(content)  # Validate and clean the content
        return self.confluence.update_page(page_id=page_id, title=title, body=clean_content)

    def retrieve_confluence_pages(self, space_key, limit=50):
        """
        Retrieve pages from a specified Confluence space using pagination.

        Args:
        space_key (str): The key of the Confluence space.
        limit (int): The number of items to retrieve per page.

        Returns:
        list: A list of page data objects.
        """
        # Implementation goes here

    def retrieve_child_items(self, item_id, content_type, limit=50):
        """
        Retrieve child items (pages or comments) for a given Confluence item using pagination.

        Args:
        item_id (str): The ID of the Confluence item (page or comment).
        content_type (str): Type of content to retrieve ('page' or 'comment').
        limit (int): The number of items to retrieve per page.

        Returns:
        list: A list of child item data objects.
        """
        # Implementation goes here

    def retrieve_space_list(self):
        """
        Retrieve a complete list of available spaces in Confluence using pagination.

        Returns:
        list: A comprehensive list of space data objects.
        """
        all_spaces = []
        start = 0
        limit = 50  # Set a reasonable default limit for each API request

        while True:
            response = self.confluence.get_all_spaces(start=start, limit=limit,
                                                      expand='description.plain,body.view,value')
            spaces = response.get('results', [])
            if not spaces:
                break  # Exit loop if no more spaces are returned

            all_spaces.extend(spaces)
            start += len(spaces)  # Increment start for the next page

        return all_spaces

    def space_exists_by_name(self, space_name):
        all_spaces = self.retrieve_space_list()
        return any(space['name'] == space_name for space in all_spaces)

    def create_space_if_not_found(self, space_name, space_key=None):
        """
        Checks if a space with the given name exists and creates it if not.
        Args:
            space_name (str): The name of the space to find or create.
            space_key (str): The key for the space to create. If not provided, a key is generated from the space name.
        Returns:
            str: The key of the existing or newly created space.
        """
        try:
            # Check if the space exists by name
            if self.space_exists_by_name(space_name):
                # If the space exists, return its key
                for space in self.retrieve_space_list():
                    if space['name'] == space_name:
                        return space['key']
            else:
                # If the space doesn't exist, create a new one
                if space_key is None:
                    space_key = self.generate_space_key(space_name)
                print(f"Creating space with key: {space_key}, abd name: {space_name}")
                self.confluence.create_space(space_key=space_key, space_name=space_name)
                return space_key
        except Exception as e:
            logging.error("Error creating space: %s", e, exc_info=True)

    def create_page(self, space_key, title, content, parent_id=None):
        """
        Create a new page in the specified Confluence space.

        Args:
            space_key (str): The key of the space where the page will be created.
            title (str): The title of the new page.
            content (str): The content of the new page.
            parent_id (int): The ID of the parent page under which the new page will be created (optional).

        Returns:
            dict: Response from the Confluence API.
        """
        clean_content = self.validate_and_coerce_xhtml(content)  # Validate and clean the content
        clean_title = self.validate_and_coerce_xhtml(title)
        return self.confluence.create_page(
            space=space_key,
            title=clean_title,
            body=clean_content,
            parent_id=parent_id,
            type='page'
        )


    @staticmethod
    def generate_space_key(space_name):
        # Create a base space key by taking the first two letters of each word
        base_key = ''.join(word[:2].upper() for word in space_name.split())
        # Append a timestamp to the base key
        timestamp = int(time.time())
        return f"{base_key}{timestamp}"

    def retrieve_page_history(self, page_id):
        """
        Retrieve the history of a specified Confluence page.

        Args:
        page_id (str): The ID of the Confluence page.

        Returns:
        dict: A dictionary containing the history of the page.
        """
        # Implementation goes here

    def retrieve_page_content(self, page_id):
        """
        Retrieve the content of a specified Confluence page.

        Args:
        page_id (str): The ID of the Confluence page.

        Returns:
        str: The content of the page.
        """
        # Implementation goes here


conf_client = ConfluenceClient()
conf_client.create_space_if_not_found(space_name="Nur documentation QnA")