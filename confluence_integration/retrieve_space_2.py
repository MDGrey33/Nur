import logging
import json
from datetime import datetime
from bs4 import BeautifulSoup
from confluence_integration.confluence_client import ConfluenceClient
from confluence_integration.retrieve_space import format_page_content_for_llm
from file_system.file_manager import FileManager
from database.page_manager import store_pages_data

confluence_client = ConfluenceClient()

def choose_space():
    """Prompt the user to choose a Confluence space from a list of available spaces."""
    spaces = confluence_client.retrieve_space_list()
    for i, space in enumerate(spaces):
        print(f"{i + 1}. {space['name']} (Key: {space['key']})")
    choice = int(input("Choose a space (number): ")) - 1
    return spaces[choice]["key"], spaces[choice]["name"]

def get_all_pages_from_space(space_key):
    """Retrieve all pages from a specified Confluence space using pagination."""
    pages = []
    start = 0
    limit = 50
    while True:
        try:
            response = confluence_client.get_all_pages_from_space(space_key, start=start, limit=limit, expand="body.storage,history,version")
            if not response:
                print(f"No pages found in space {space_key}.")
                break
            pages.extend(response)  # Assuming response is already a list of dictionaries
            if len(response) < limit:
                break
            start += limit
        except Exception as e:
            logging.error(f"Failed to retrieve pages from {space_key} starting at {start}: {e}")
            break
    return pages

def strip_html_tags(content):
    """Remove HTML tags from a string."""
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text()

def get_comments_for_page(page_id):
    """Retrieve all comments for a specified page using pagination."""
    comments = []
    start = 0
    limit = 50  # Adjust based on your preference or API limits
    while True:
        try:
            fetched_comments = confluence_client.get_page_child_by_type(page_id, type="comment", start=start, limit=limit)
            print(f"Fetched {len(fetched_comments)} comments for page {page_id} starting at {start}")
            if not fetched_comments:
                break
            comments.extend(fetched_comments)
            if len(fetched_comments) < limit:
                break  # Break the loop if there are no more comments to fetch
            start += limit
        except Exception as e:
            logging.error(f"Failed to retrieve comments for page {page_id} starting at {start}: {e}")
            break
    return comments

def get_comment_content(comment_id):
    """Retrieve the content of a comment."""
    try:
        comment = confluence_client.get_page_by_id(comment_id, expand="body.storage")
        comment_content = comment.get("body", {}).get("storage", {}).get("value", "")
        comment_text = strip_html_tags(comment_content)
        return comment_text
    except Exception as e:
        logging.error(f"Error retrieving content for comment ID {comment_id}: {e}")
        return ""  # Return empty string if an error occurs

def format_comment(comment):
    """Format a comment for storage."""
    try:
        comment_text = get_comment_content(comment['id'])
        return {
            'id': comment['id'],
            'author': comment.get('history', {}).get('createdBy', {}).get('displayName', 'Unknown'),
            'createdDate': comment.get('history', {}).get('createdDate', 'Unknown'),
            'content': comment_text
        }
    except KeyError as e:
        logging.error(f"Missing key in comment {comment['id']}: {e}")
        return {
            'id': comment['id'],
            'author': 'Unknown',
            'createdDate': 'Unknown',
            'content': 'No content'
        }

def process_page(page, space_key):
    """Process a page and store its data in files and a database."""
    current_time = datetime.now()
    file_manager = FileManager()

    try:
        page_id = page["id"]
        page_title = strip_html_tags(page["title"])
        page_author = page["history"]["createdBy"]["displayName"]
        created_date = page["history"]["createdDate"]
        last_updated = page["version"]["when"]
        page_content = strip_html_tags(page.get("body", {}).get("storage", {}).get("value", ""))

        # Add page comments to page_data
        raw_comments = get_comments_for_page(page_id)
        formatted_comments = [format_comment(comment) for comment in raw_comments]
        comments = json.dumps(formatted_comments)

        page_data = {
            "spaceKey": space_key,
            "pageId": page_id,
            "title": page_title,
            "author": page_author,
            "createdDate": created_date,
            "lastUpdated": last_updated,
            "content": page_content,
            "datePulledFromConfluence": current_time,
            "comments": comments,
        }

        formatted_content = format_page_content_for_llm(page_data)
        file_manager.create(f"{page_id}.txt", formatted_content)

        # verify page_data is consistent with the database schema
        store_pages_data(space_key, {page_id: page_data})

        return page_data
    except Exception as e:
        logging.error(f"Error processing page: {e}")
        return None

def get_space_content(space_key):
    """Retrieve and process all pages from a specified Confluence space."""
    all_pages = get_all_pages_from_space(space_key)
    processed_pages = [process_page(page, space_key) for page in all_pages]
    # Here you would insert processed_pages into your database and vector DB

    print(f"Processed {len(processed_pages)} pages from space {space_key}.")
    return processed_pages

if __name__ == "__main__":
    space_key, space_name = choose_space()
    processed_pages = get_space_content(space_key)