import os

from atlassian import Confluence

from datetime import datetime

from app.knowledge_sources.confluence.confluence_helper import ConfluenceHelper
from openai import OpenAI

from app.knowledge_sources.models.knowledge_source import KnowledgeSource
from app.knowledge_sources.models.knowledge_source_item import KnowledgeSourceItem
from app.knowledge_sources.confluence.requests.confluence_options import ConfluenceOptions
from app.storage.storage_manager import StorageManager

import chromadb
from chromadb.config import Settings


class ConfluenceSource:
    def __init__(self, options: ConfluenceOptions, open_ai_client: OpenAI):
        self.options = options
        self.open_ai_client = open_ai_client
        self.confluence_helper = self.get_confluence_helper()
        self.storageManager = StorageManager()

    def get_confluence_helper(self):
        confluence = Confluence(
            url=self.options.base_url,
            username=self.options.username,
            password=self.options.access_token
        )

        return ConfluenceHelper(confluence)

    def process(self):
        chroma_client = chromadb.HttpClient(host="127.0.0.1", port=8001,
                                            settings=Settings(allow_reset=True, anonymized_telemetry=False))

        global_knowledge_collection = chroma_client.get_or_create_collection(name="global_knowledge_collection")

        knowledge_source = KnowledgeSource(user_id=1, source_type=1).get_or_create()

        space_pages = self.confluence_helper.get_pages_from_space(self.options.space_key)

        for space_page in space_pages:
            space_page_data = self.confluence_helper.get_page_by_id(space_page['id'])
            page_body = self.confluence_helper.get_page_body(space_page_data)
            page_comments = self.confluence_helper.get_page_comments(space_page['id'])

            knowledge_source_item = KnowledgeSourceItem(
                external_identifier=space_page_data['id'],
                source_id=knowledge_source.id,
                title=space_page_data['title'],
                author=space_page_data['history']['createdBy']['displayName'],
                created_at=datetime.strptime(space_page_data['history']['createdDate'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                updated_at=datetime.strptime(space_page_data['version']['when'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                file_identifier='confluence' + self.options.space_key + space_page_data['id']
            )

            knowledge_source_item.get_or_create()

            final_page_content = 'body: ' + page_body + '\n' + 'comments: ' + ", ".join(page_comments)

            embedding_json = self.open_ai_client.embeddings.create(input=final_page_content,
                                                                   model='text-embedding-3-large')
            embedding_vector = embedding_json.dict()["data"][0]["embedding"]

            embedding_vector

            embeddings = [
                embedding_vector
            ]

            ids = [space_page['id']]

            global_knowledge_collection.upsert(embeddings=embeddings, ids=ids)
            a = global_knowledge_collection.get(ids=ids, include=['embeddings'])

            # return a
            #
            # self.storageManager.create_file(knowledge_source_item.file_identifier, final_page_content)

        return "ok"
