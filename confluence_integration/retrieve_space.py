import json
from datetime import datetime
from bs4 import BeautifulSoup
from atlassian import Confluence
from credentials import confluence_credentials
from database.confluence_database import store_space_data, store_pages_data

# Initialize Confluence API
confluence = Confluence(
    url=confluence_credentials['base_url'],
    username=confluence_credentials['username'],
    password=confluence_credentials['api_token']
)


# Get top level pages from a space
def get_top_level_ids(space_key):
    top_level_pages = confluence.get_all_pages_from_space(space_key)
    return [page['id'] for page in top_level_pages]


# Get child pages from a page
def get_child_ids(item_id, content_type):
    child_items = confluence.get_page_child_by_type(item_id, type=content_type)
    return [child['id'] for child in child_items]


def get_all_pages_recursive(space_key):
    def get_child_pages_recursively(page_id):
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


def get_all_comments_recursive(page_id):
    def get_child_comments_recursively(comment_id):
        child_comments = []
        child_comment_ids = get_child_ids(comment_id, content_type='comment')
        for child_id in child_comment_ids:
            child_comments.append(child_id)
            child_comments.extend(get_child_comments_recursively(child_id))
        return child_comments

    all_comments = []
    top_level_comment_ids = get_child_ids(page_id, content_type='comment')
    for comment_id in top_level_comment_ids:
        all_comments.append(comment_id)
        all_comments.extend(get_child_comments_recursively(comment_id))
    return all_comments


"""
def get_space_ids(space_key):
    all_page_ids = get_all_pages_recursive(space_key)
    page_comments_map = {}

    for page_id in all_page_ids:
        page_comments = get_all_comments_recursive(page_id)
        page_comments_map[page_id] = page_comments

    print("Page and Comments Map:", page_comments_map)
"""


def choose_space():
    spaces = confluence.get_all_spaces(start=0, limit=50, expand='description.plain,body.view,value')
    for i, space in enumerate(spaces['results']):
        print(f"{i + 1}. {space['name']} (Key: {space['key']})")
    choice = int(input("Choose a space (number): ")) - 1
    space_key = spaces['results'][choice]['key']
    space_data={'space_key': space_key,
                'url': confluence_credentials['base_url'],
                'login': confluence_credentials['username'],
                'token': confluence_credentials['api_token']
                }
    store_space_data(space_data)
    return spaces['results'][choice]['key']


def strip_html_tags(content):
    soup = BeautifulSoup(content, 'html.parser')
    return soup.get_text()


def check_date_filter(update_date, all_page_ids):
    updated_pages = []
    for page_id in all_page_ids:
        page_history = confluence.history(page_id)  # directly use page_id
        last_updated = datetime.strptime(page_history['lastUpdated']['when'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if last_updated >= update_date:
            updated_pages.append(page_id)  # append the page_id to the list
    return updated_pages



def get_space_content(update_date=None):
    space_key = choose_space()
    all_page_ids = get_all_pages_recursive(space_key)
    if update_date is not None:
        all_page_ids = check_date_filter(update_date, all_page_ids)
    page_content_map = {}

    for page_id in all_page_ids:
        page = confluence.get_page_by_id(page_id, expand='body.storage,history,version')
        page_title = strip_html_tags(page['title'])

        page_author = page['history']['createdBy']['displayName']
        created_date = page['history']['createdDate']
        last_updated = page['version']['when']

        page_content = strip_html_tags(page.get('body', {}).get('storage', {}).get('value', ''))

        page_comments_content = ""
        page_comments = get_all_comments_recursive(page_id)
        for comment_id in page_comments:
            comment = confluence.get_page_by_id(comment_id, expand='body.storage')
            comment_content = comment.get('body', {}).get('storage', {}).get('value', '')
            page_comments_content += strip_html_tags(comment_content)

        page_content_map[page_id] = {
            'title': page_title,
            'author': page_author,
            'createdDate': created_date,
            'lastUpdated': last_updated,
            'content': page_content,
            'comments': page_comments_content
        }

    with open('page_content.json', 'w') as f:
        json.dump(page_content_map, f)

    store_pages_data(space_key, page_content_map)
    print("Page content written to JSON and database.")

    return page_content_map


if __name__ == "__main__":
    # Initial space retrieve
    get_space_content()
    # Space update retrieve
    # get_space_content(update_date=datetime(2023, 12, 1, 0, 0, 0))

