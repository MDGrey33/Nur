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


# Get a list of all ids of content items of all types in space and the ids of their children
def get_all_ids(confluence, space_key):
    # Recursively fetch child ids of a page
    def get_child_ids(page_id):
        child_ids = []
        # Fetch child pages
        children = confluence.get_page_child_by_type(page_id, type='page')
        for child in children:
            child_ids.append(child['id'])
            # Recursively fetch children of the child page
            child_ids.extend(get_child_ids(child['id']))

        # Fetch comments
        comments = confluence.get_page_child_by_type(page_id, type='comment')
        for comment in comments:
            child_ids.append(comment['id'])
        return child_ids

    all_ids = []
    pages = confluence.get_all_pages_from_space(space_key)
    for page in pages:
        page_id = page['id']
        all_ids.append(page_id)
        all_ids.extend(get_child_ids(page_id))

    return all_ids


def get_page_details_with_comments(confluence, all_ids_with_comments):
    pages_details = {}

    for page_id, comment_ids in all_ids_with_comments.items():
        page = confluence.get_page_by_id(page_id, expand='body.storage,title')
        title = page['title']
        body = page['body']['storage']['value']

        comments_content = []
        for comment_id in comment_ids:
            comment = confluence.get_content_by_id(comment_id, expand='body.storage,history.createdBy')
            comment_text = comment['body']['storage']['value']
            commenter = comment['history']['createdBy']['displayName']
            created_date = comment['history']['createdDate']
            comments_content.append(f"Comment by {commenter} on {created_date}: {comment_text}")

        pages_details[page_id] = {'title': title, 'body': body, 'comments': comments_content}

    return pages_details



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


def get_page_comments(confluence, page_id):
    comments = confluence.get_page_child_by_type(page_id, type='comment')
    print(comments)


def create_page(confluence, space, title, body):
    new_page = confluence.create_page(space, title, body)
    print(new_page)


def create_comment(confluence, page_id, comment):
    confluence.add_comment(page_id, comment)
    print(comment)


def test_read_content():
    get_list_of_spaces(confluence)

    space_key = 'ST'

    get_pages_in_space(confluence, space_key)

    page_id = 33250  # Replace with your page ID

    get_page_content_and_comments(confluence, page_id)

    get_page_comments(confluence, page_id)

    print(get_all_ids(confluence, space_key))


def test_create_content():
    space_key = 'ST'
    page_id = 33250  # Replace with your page ID

    for i in range(1, 10):
        title = f"New Pages {i}"
        body = "This is the body of our new page.{i}"
        create_page(confluence, space_key, title, body)
        for j in range(1, 3):
            comment = f'Your comment text here.{i}'
            print(create_comment(confluence, page_id, comment))


test_read_content()
