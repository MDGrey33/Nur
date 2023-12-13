# ./confluence_integration/retrieve_space.py
from datetime import datetime
from bs4 import BeautifulSoup
from atlassian import Confluence
from credentials import confluence_credentials
from database.confluence_database import store_space_data, store_page_data
from file_system.file_manager import FileManager
from messaging_service.pulsar_client import PulsarClient
from configuration import pulsar_client_url

pulsar_client = PulsarClient(pulsar_client_url)

# Initialize Confluence API
confluence = Confluence(
    url=confluence_credentials['base_url'],
    username=confluence_credentials['username'],
    password=confluence_credentials['api_token']
)


# Get top level pages from a space
def get_top_level_ids(space_key):
    """
    Retrieve IDs of top-level pages in a specified Confluence space.

    Args:
    space_key (str): The key of the Confluence space.

    Returns:
    list: A list of page IDs for the top-level pages in the space.
    """
    top_level_pages = confluence.get_all_pages_from_space(space_key)
    return [page['id'] for page in top_level_pages]


# Get child pages from a page
def get_child_ids(item_id, content_type):
    """
    Retrieve IDs of child items (pages or comments) for a given Confluence item.

    Args:
    item_id (str): The ID of the Confluence page or comment.
    content_type (str): Type of content to retrieve ('page' or 'comment').

    Returns:
    list: A list of IDs for child items.
    """
    child_items = confluence.get_page_child_by_type(item_id, type=content_type)
    return [child['id'] for child in child_items]


def get_all_page_ids_recursive(space_key):
    def get_child_pages_recursively(page_id):
        child_pages = []
        child_page_ids = get_child_ids(page_id, content_type='page')
        for child_id in child_page_ids:
            child_pages.append(child_id)
            child_pages.extend(get_child_pages_recursively(child_id))
        return child_pages

    all_page_ids = []
    top_level_ids = get_top_level_ids(space_key)
    topic_name = "confluence_page_ids"  # Define the topic name here

    for top_level_id in top_level_ids:
        all_page_ids.append(top_level_id)
        all_page_ids.extend(get_child_pages_recursively(top_level_id))

    for page_id in all_page_ids:
        pulsar_client.publish_message(topic_name, str(page_id))  # Include the topic name

    return all_page_ids


def get_all_comment_ids_recursive(page_id):
    """
    Recursively retrieves all comment IDs for a given Confluence page.

    Args:
    page_id (str): The ID of the Confluence page.

    Returns:
    list: A list of all comment IDs for the page.
    """

    def get_child_comment_ids_recursively(comment_id):
        # Inner function to recursively get child comment IDs
        child_comment_ids = []  # Use a separate list to accumulate child comment IDs
        immediate_child_ids = get_child_ids(comment_id, content_type='comment')
        for child_id in immediate_child_ids:
            child_comment_ids.append(child_id)
            child_comment_ids.extend(get_child_comment_ids_recursively(child_id))
        return child_comment_ids

    all_comment_ids = []
    top_level_comment_ids = get_child_ids(page_id, content_type='comment')
    for comment_id in top_level_comment_ids:
        all_comment_ids.append(comment_id)
        all_comment_ids.extend(get_child_comment_ids_recursively(comment_id))
    return all_comment_ids


def choose_space():
    """
    Prompt the user to choose a Confluence space from a list of available spaces.

    Returns:
    str: The key of the chosen Confluence space.
    """
    spaces = confluence.get_all_spaces(start=0, limit=50, expand='description.plain,body.view,value')
    for i, space in enumerate(spaces['results']):
        print(f"{i + 1}. {space['name']} (Key: {space['key']})")
    choice = int(input("Choose a space (number): ")) - 1
    space_key = spaces['results'][choice]['key']
    space_data = {'space_key': space_key,
                  'url': confluence_credentials['base_url'],
                  'login': confluence_credentials['username'],
                  'token': confluence_credentials['api_token']
                  }
    store_space_data(space_data)
    return spaces['results'][choice]['key']


def strip_html_tags(content):
    """
    Remove HTML tags from a string.

    Args:
    content (str): The string with HTML content.

    Returns:
    str: The string with HTML tags removed.
    """
    soup = BeautifulSoup(content, 'html.parser')
    return soup.get_text()


def check_date_filter(update_date, all_page_ids):
    """
    Filter pages based on their last updated date.

    Args:
    update_date (datetime): The threshold date for filtering. Pages updated after this date will be included.
    all_page_ids (list): A list of page IDs to be filtered.

    Returns:
    list: A list of page IDs that were last updated on or after the specified update_date.
    """
    updated_pages = []
    for page_id in all_page_ids:
        page_history = confluence.history(page_id)  # directly use page_id
        last_updated = datetime.strptime(page_history['lastUpdated']['when'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if last_updated >= update_date:
            updated_pages.append(page_id)  # append the page_id to the list
    return updated_pages


def format_page_content_for_llm(page_data):
    """
        Format page data into a string of key-value pairs suitable for LLM (Language Learning Models) context.

        This function converts page data into a text format that can be easily consumed by language models,
        with each key-value pair on a separate line.

        Args:
        page_data (dict): A dictionary containing page data with keys like title, author, createdDate, etc.

        Returns:
        str: A string representation of the page data in key-value format.
        """
    content = ""
    for key, value in page_data.items():
        content += f"{key}: {value}\n"
    return content


def publish_space_ids(space_key, update_date=None):
    topic_name = "confluence_page_ids"
    all_page_ids = get_all_page_ids_recursive(space_key)
    if update_date is not None:
        all_page_ids = check_date_filter(update_date, all_page_ids)

    for page_id in all_page_ids:
        pulsar_client.publish_message(topic_name, str(page_id))

    print("Page IDs published to Pulsar.")
    return all_page_ids


def retrieve_and_process_page_data(page_id, space_key):
    page = confluence.get_page_by_id(page_id, expand='body.storage,history,version')
    if not page:
        print(f"No data found for page ID: {page_id}")
        return

    page_title = page.get('title', '')
    page_author = page.get('history', {}).get('createdBy', {}).get('displayName', '')
    created_date = page.get('history', {}).get('createdDate', '')
    last_updated = page.get('version', {}).get('when', '')
    page_content = strip_html_tags(page.get('body', {}).get('storage', {}).get('value', ''))

    page_comments_content = ""
    page_comment_ids = get_all_comment_ids_recursive(page_id)
    for comment_id in page_comment_ids:
        comment = confluence.get_page_by_id(comment_id, expand='body.storage')
        comment_content = strip_html_tags(comment.get('body', {}).get('storage', {}).get('value', ''))
        page_comments_content += comment_content + '\n'

    page_data = {
        'title': page_title,
        'author': page_author,
        'createdDate': created_date,
        'lastUpdated': last_updated,
        'content': page_content,
        'comments': page_comments_content
    }

    store_page_data(page_id, space_key, page_data)
    formatted_content = format_page_content_for_llm(page_data)
    file_manager = FileManager()
    file_manager.create(f"{page_id}.txt", formatted_content)


def consume_pages_and_store_data(topic_name, subscription_name, space_key):
    while True:
        page_id = pulsar_client.consume_message(topic_name, subscription_name)
        if page_id:
            retrieve_and_process_page_data(page_id, space_key)
    pulsar_client.close()


if __name__ == "__main__":
    chosen_space_key = choose_space()
    publish_space_ids(chosen_space_key)
    consume_pages_and_store_data("confluence_page_ids", "default_processor", chosen_space_key)
