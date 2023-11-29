import requests
import json
from atlassian import Confluence
from credentials import confluence_credentials

# Initialize Confluence API
confluence = Confluence(
    url=confluence_credentials['base_url'],
    username=confluence_credentials['username'],
    password=confluence_credentials['api_token']
)


def get_all_ids(confluence, space_key):
    # Function to fetch child IDs for a page
    def get_child_ids(page_id):
        child_ids = []
        # Fetch comments
        comments = confluence.get_page_child_by_type(page_id, type='comment')
        for comment in comments:
            child_ids.append(comment['id'])
        return child_ids

    all_ids = []
    # Fetch top-level pages
    pages = confluence.get_all_pages_from_space(space_key, content_type='page')
    for page in pages:
        page_id = page['id']
        all_ids.append((page_id, get_child_ids(page_id)))

    return all_ids


def get_page_details_with_comments(confluence, all_ids):
    pages_details = {}
    for page_id, comment_ids in all_ids:
        page = confluence.get_page_by_id(page_id, expand='body.storage,title')
        title = page['title']
        body = page['body']['storage']['value']

        comments_content = []
        for comment_id in comment_ids:
            comment = confluence.get_page_by_id(comment_id, expand='body.storage,history.createdBy')
            comment_text = comment['body']['storage']['value']
            comments_content.append(comment_text)

        pages_details[page_id] = {'title': title, 'body': body, 'comments': comments_content}

    return pages_details


def summarize_comments_with_llm(page_content, comments):
    system_prompt = """
    Focus strictly on the content provided. Avoid assumptions or adding information not present in the comments. Maintain the style and language used in the comments.
    """
    user_prompt = f"""
    Given the content of a page: 
    {page_content}
    And the associated comments: 
    {comments}
    Please provide a summary of the comments with the following considerations:
    
    1. Identify the key themes discussed in the comments.
    2. Highlight any new insights or additional information that the comments provide, which are not covered in the page content.
    3. Pay attention to any questions raised in the comments and the answers provided.
    4. Note any points of agreement or disagreement among the commenters.
    5. Summarize these elements concisely to enhance the understanding of the page's content.
    """
    print(f"System Prompt: {system_prompt}")
    print(f"User Prompt: {user_prompt}")
    # API call to local LLM
    response = requests.post(
        'http://localhost:1234/v1/chat/completions',
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False
        })
    )

    return response.json()


def choose_space(confluence):
    spaces = confluence.get_all_spaces(start=0, limit=50, expand='description.plain,body.view,value')
    for i, space in enumerate(spaces['results']):
        print(f"{i + 1}. {space['name']} (Key: {space['key']})")
    choice = int(input("Choose a space (number): ")) - 1
    return spaces['results'][choice]['key']


# Example Usage
chosen_space_key = choose_space(confluence)
all_ids_with_comments = get_all_ids(confluence, chosen_space_key)
pages_details = get_page_details_with_comments(confluence, all_ids_with_comments)

for page_id, details in pages_details.items():
    if details['comments']:  # Check if there are comments
        page_content = details['body']
        comments = " ".join(details['comments'])
        summarized_comments = summarize_comments_with_llm(page_content, comments)
        print(f"Page: {details['title']}")
        print(f"Summarized Comments: {summarized_comments['choices'][0]['message']['content']}")
    else:
        print(f"Page: {details['title']}")
        print("No comments to summarize.")
