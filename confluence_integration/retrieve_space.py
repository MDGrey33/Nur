# ./confluence_integration/retrieve_space.py
import os
from datetime import datetime
from bs4 import BeautifulSoup
from atlassian import Confluence
from credentials import confluence_credentials
from database.nur_database import mark_page_as_processed
from persistqueue import Queue
from configuration import persist_page_processing_queue_path
from confluence_integration.confluence_client import ConfluenceClient

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
    """
    Recursively retrieves all page IDs in a given space, including child pages.

    Args:
    space_key (str): The key of the Confluence space.

    Returns:
    list: A list of all page IDs in the space.
    """

    def get_child_pages_recursively(page_id):
        # Inner function to recursively get child page IDs
        child_pages = []
        child_page_ids = get_child_ids(page_id, content_type='page')
        for child_id in child_page_ids:
            child_pages.append(child_id)
            child_pages.extend(get_child_pages_recursively(child_id))
        return child_pages

    all_pages = []
    top_level_ids = get_top_level_ids(space_key)
    for top_level_id in top_level_ids:
        all_pages.append(top_level_id)
        all_pages.extend(get_child_pages_recursively(top_level_id))

    return all_pages


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

    Args:
    confluence_client (ConfluenceClient): The Confluence client object.

    Returns:
    str: The key of the chosen Confluence space.
    """
    confluence_client = ConfluenceClient()
    spaces = confluence_client.retrieve_space_list()
    for i, space in enumerate(spaces):
        print(f"{i + 1}. {space['name']} (Key: {space['key']})")
    choice = int(input("Choose a space (number): ")) - 1
    return spaces[choice]['key']


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


def get_comment_content(comment_id):
    """
    Retrieve the content of a comment.

    Args:
    comment_id (str): The ID of the comment.

    Returns:
    str: The content of the comment.
    """
    comment = confluence.get_page_by_id(comment_id, expand='body.storage')
    comment_content = comment.get('body', {}).get('storage', {}).get('value', '')
    comment_text = strip_html_tags(comment_content)
    return comment_text


def process_page(page_id, space_key, file_manager, page_content_map):
    """
    Process a page and store its data in files and a database.
    :param page_id:
    :param space_key:
    :param file_manager:
    :param page_content_map:
    :return: page_data
    """
    current_time = datetime.now()
    page = confluence.get_page_by_id(page_id, expand='body.storage,history,version')
    page_title = strip_html_tags(page['title'])
    page_author = page['history']['createdBy']['displayName']
    created_date = page['history']['createdDate']
    last_updated = page['version']['when']
    page_content = strip_html_tags(page.get('body', {}).get('storage', {}).get('value', ''))
    page_comments_content = ""
    page_comment_ids = get_all_comment_ids_recursive(page_id)

    for comment_id in page_comment_ids:
        page_comments_content += get_comment_content(comment_id)

    page_data = {
        'spaceKey': space_key,
        'pageId': page_id,
        'title': page_title,
        'author': page_author,
        'createdDate': created_date,
        'lastUpdated': last_updated,
        'content': page_content,
        'comments': page_comments_content,
        'datePulledFromConfluence': current_time
    }

    # Store data for files
    formatted_content = format_page_content_for_llm(page_data)
    file_manager.create(f"{page_id}.txt", formatted_content)  # Create a file for each page
    print(f"Page with ID {page_id} processed and written to file.")

    # Store data for database
    page_content_map[page_id] = page_data
    print(f"Page with ID {page_id} processed and written database.")

    # Mark the page as processed
    mark_page_as_processed(page_id)
    return page_data


def get_space_content(update_date=None):
    """
    Retrieve content from a specified Confluence space and process it.

    This function allows the user to choose a Confluence space, retrieves all relevant page and comment data,
    formats it, and stores it both in files and a database.

    Args:
    update_date (datetime, optional): If provided, only pages updated after this date will be retrieved. Default is None.

    Returns:
    list: A list of IDs of all pages that were processed.
    """

    space_key = choose_space()
    all_page_ids = get_all_page_ids_recursive(space_key)
    all_page_ids = set(all_page_ids)

    if update_date is not None:
        all_page_ids = check_date_filter(update_date, all_page_ids)

    # Setting up the persist-queue
    queue_path = os.path.join(persist_page_processing_queue_path, space_key)
    page_queue = Queue(queue_path)
    # make all page ids a set to eliminate duplicates
    for page_id in all_page_ids:
        page_queue.put(page_id)

    print(f"Enqueued {len(all_page_ids)} pages for processing.")
    print(f"Pages queued {all_page_ids}")
    return space_key


if __name__ == "__main__":

    # Initial space retrieve
    space_key = get_space_content()
    # Initial space retrieve
    # Space update retrieve
    # get_space_content(update_date=datetime(2023, 12, 1, 0, 0, 0))
