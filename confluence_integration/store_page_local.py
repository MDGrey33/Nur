import logging
logging.basicConfig(level=logging.DEBUG)
from confluence_integration.confluence_client import ConfluenceClient
from file_system.file_manager import FileManager
from database.page_manager import store_pages_data, parse_datetime

def store_page_locally_from_confluence(page_id, space_key):
    """
    Pulls the page from Confluence, stores it as a .txt file, and adds it to the page_data table in the DB.
    """
    confluence_client = ConfluenceClient()
    file_manager = FileManager()

    # 1. Pull the page content from Confluence
    page = confluence_client.confluence.get_page_by_id(page_id, expand="body.storage,history,version")
    if not page:
        logging.error(f"Could not retrieve page with ID {page_id} from Confluence.")
        raise Exception(f"Could not retrieve page with ID {page_id} from Confluence.")

    # 2. Extract metadata (snake_case, matching the model)
    page_title = page["title"]
    page_author = page["history"]["createdBy"]["displayName"]
    created_date = parse_datetime(page["history"]["createdDate"])
    last_updated = parse_datetime(page["version"]["when"])
    page_content = page.get("body", {}).get("storage", {}).get("value", "")
    page_comments_content = ""  # (Optional: pull comments if needed)
    date_pulled_from_confluence = created_date  # Or use datetime.now(timezone.utc) if you want the pull time

    # 3. Prepare the page_data dict with correct keys
    page_data = {
        "page_id": page_id,
        "space_key": space_key,
        "title": page_title,
        "author": page_author,
        "createdDate": created_date,
        "lastUpdated": last_updated,
        "content": page_content,
        "comments": page_comments_content,
        "date_pulled_from_confluence": date_pulled_from_confluence,
    }

    # 4. Store as .txt file
    formatted_content = (
        f"spaceKey: {space_key}\n"
        f"pageId: {page_id}\n"
        f"title: {page_title}\n"
        f"author: {page_author}\n"
        f"createdDate: {created_date.isoformat()}\n"
        f"lastUpdated: {last_updated.isoformat()}\n"
        f"content: {page_content}\n"
        f"comments: {page_comments_content}\n"
        f"datePulledFromConfluence: {date_pulled_from_confluence}\n"
    )
    file_manager.create(f"{page_id}.txt", formatted_content)
    logging.info(f"Stored page {page_id} as .txt file.")

    # 5. Add to DB (as a dict of {page_id: page_data})
    # Use the same structure as retrieve_space: keys must be 'createdDate', 'lastUpdated', 'datePulledFromConfluence', etc.
    # Let store_pages_data handle the mapping and parsing as in retrieve_space
    page_data_for_db = {
        "title": page_title,
        "author": page_author,
        "createdDate": created_date.isoformat(),
        "lastUpdated": last_updated.isoformat(),
        "content": page_content,
        "comments": page_comments_content,
        "date_pulled_from_confluence": date_pulled_from_confluence,
    }
    print(f"page_data being stored: {page_data_for_db}")
    store_pages_data(space_key, {page_id: page_data_for_db})
    logging.info(f"Added page {page_id} to page_data table in DB.") 