from atlassian import Confluence
from bs4 import BeautifulSoup

from app.database.database import get_db
from datetime import datetime
from app.knowledge_sources.confluence.models.knowledge_source import KnowledgeSource
from app.knowledge_sources.confluence.models.knowledge_source_item import KnowledgeSourceItem
from app.knowledge_sources.confluence.requests.confluence_options import ConfluenceOptions
from app.storage.storage_manager import StorageManager


class ConfluenceSource:
    def __init__(self, options: ConfluenceOptions):
        self.options = options
        self.confluence = self.get_confluence()

    def get_confluence(self):
        confluence = Confluence(
            url=self.options.base_url,
            username=self.options.username,
            password=self.options.access_token
        )

        return confluence

    def process(self):
        space_pages = self.confluence.get_all_pages_from_space(self.options.space_key)
        db = get_db()

        ks = KnowledgeSource(user_id=1, source_type=1)
        db.add(ks)
        db.commit()

        for space_page in space_pages:
            space_page_data = self.confluence.get_page_by_id(space_page['id'], expand='body.storage,history,version')

            ksi=KnowledgeSourceItem(
                external_identifier=space_page_data['id'],
                source_id=ks.id,
                title=space_page_data['title'],
                author=space_page_data['history']['createdBy']['displayName'],
                created_at=datetime.strptime(space_page_data['history']['createdDate'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                updated_at=datetime.strptime(space_page_data['version']['when'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                file_identifier='confluence' + self.options.space_key + space_page_data['id']
            )
            db.add(ksi)
            db.commit()

            page_content = self.strip_html_tags(space_page_data.get('body', {}).get('storage', {}).get('value', ''))
            page_comments = self.confluence.get_page_child_by_type(space_page['id'], 'comment')

            sm = StorageManager()
            sm.create_file(ksi.file_identifier, page_content)

        return "ok"

    def strip_html_tags(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        return soup.get_text()
