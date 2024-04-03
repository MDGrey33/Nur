from bs4 import BeautifulSoup


class ConfluenceHelper:

    def __init__(self, confluence):
        self.confluence = confluence

    def get_pages_from_space(self, space_key):
        return self.confluence.get_all_pages_from_space(space_key)

    def get_page_by_id(self, page_id):
        return self.confluence.get_page_by_id(page_id, expand='body.storage,history,version')

    def get_page_body(self, page):
        return self.strip_html_tags(page.get('body', {}).get('storage', {}).get('value', ''))

    def strip_html_tags(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        return soup.get_text()

    def get_page_comments(self, page_id):
        page_comments = []
        all_comments = []
        top_level_comments = self.confluence.get_page_child_by_type(page_id, "comment")

        def get_child_comment_ids_recursively(comment_id):
            child_comments = []
            immediate_children = self.confluence.get_page_child_by_type(comment_id, "comment")
            for child in immediate_children:
                child_comments.append(child)
                child_comments.extend(get_child_comment_ids_recursively(child['id']))
            return child_comments

        for comment in top_level_comments:
            all_comments.append(comment)
            all_comments.extend(get_child_comment_ids_recursively(comment['id']))

        for comment in all_comments:
            comment = self.confluence.get_page_by_id(comment['id'], expand="body.storage")
            comment_content = comment.get("body", {}).get("storage", {}).get("value", "")
            comment_text = self.strip_html_tags(comment_content)
            page_comments.append(comment_text)
        return page_comments
