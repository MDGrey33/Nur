from atlassian import Confluence
from credentials import confluence_credentials

# Create a Confluence object
confluence = Confluence(
    url=confluence_credentials['base_url'],
    username=confluence_credentials['username'],
    password=confluence_credentials['api_token']
    )


def get_list_of_spaces(confluence):
    spaces_response = confluence.get_all_spaces(start=0, limit=50, expand='description.plain,body.view,value')
    for space in spaces_response['results']:
        print(f"Space Name: {space['name']}, Space Key: {space['key']}")


# Get the list of pages in a space
def get_pages_in_space(confluence, space_key):
    pages = confluence.get_all_pages_from_space(space_key, start=0, limit=50, status='current')
    for page in pages:
        print(f"Page Title: {page['title']}, Page ID: {page['id']}")


def get_page_content_and_comments(confluence, page_id):
    page_data = confluence.get_page_by_id(page_id, expand='body.storage,title')
    content = page_data['body']['storage']['value']
    title = page_data['title']

    print(f"title: {title}, \ncontent: {content}")


get_list_of_spaces(confluence)

space_key = 'ST'

get_pages_in_space(confluence, space_key)

page_id = 33250  # Replace with your page ID

get_page_content_and_comments(confluence, page_id)
