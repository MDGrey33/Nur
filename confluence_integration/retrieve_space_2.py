# ./confluence_integration/retrieve_space.py
# Used as part of loading documentation from confluence
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from confluence_integration.confluence_client import ConfluenceClient
from database.page_manager import mark_page_as_processed

from confluence_integration.retrieve_space import format_page_content_for_llm
from file_system.file_manager import FileManager


confluence_client = ConfluenceClient()


def get_all_pages_from_space(space_key):
    """Retrieve all pages from a specified Confluence space using pagination."""
    pages = []
    start = 0
    limit = 50
    while True:
        try:
            response = confluence_client.get_all_pages_from_space(space_key, start=start, limit=limit)
            new_pages = response.get('results', [])
            pages.extend(new_pages)
            if len(new_pages) < limit:
                break
            start += limit
        except Exception as e:
            logging.error(f"Failed to retrieve pages from {space_key} starting at {start}: {e}")
            break
    return pages


def choose_space():
    """Prompt the user to choose a Confluence space from a list of available spaces."""
    spaces = confluence_client.retrieve_space_list()
    for i, space in enumerate(spaces):
        print(f"{i + 1}. {space['name']} (Key: {space['key']})")
    choice = int(input("Choose a space (number): ")) - 1
    return spaces[choice]["key"], spaces[choice]["name"]


def strip_html_tags(content):
    """Remove HTML tags from a string."""
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text()


def process_page(page_id, space_key, file_manager, page_content_map):
    """Process a page and store its data in files and a database."""
    current_time = datetime.now()
    try:
        page = confluence_client.get_page_by_id(page_id, expand="body.storage,history,version")
        page_title = strip_html_tags(page["title"])
        page_author = page["history"]["createdBy"]["displayName"]
        created_date = page["history"]["createdDate"]
        last_updated = page["version"]["when"]
        page_content = strip_html_tags(page.get("body", {}).get("storage", {}).get("value", ""))

        page_data = {
            "spaceKey": space_key,
            "pageId": page_id,
            "title": page_title,
            "author": page_author,
            "createdDate": created_date,
            "lastUpdated": last_updated,
            "content": page_content,
            "datePulledFromConfluence": current_time,
        }

        formatted_content = format_page_content_for_llm(page_data)
        file_manager.create(f"{page_id}.txt", formatted_content)
        page_content_map[page_id] = page_data
        mark_page_as_processed(page_id)
    except Exception as e:
        logging.error(f"Error processing page with ID {page_id}: {e}")
        return None


def get_space_content(space_key):
    """Retrieve and process all pages from a specified Confluence space."""
    file_manager = FileManager()
    page_content_map = {}
    all_pages = get_all_pages_from_space(space_key)
    for page in all_pages:
        process_page(page['id'], space_key, file_manager, page_content_map)


if __name__ == "__main__":
    space_key, space_name = choose_space()
    get_space_content(space_key)
