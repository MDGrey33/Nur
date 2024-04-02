from fastapi import APIRouter

from app.knowledge_sources.confluence.requests.confluence_options import (
    ConfluenceOptions,
)
from app.knowledge_sources.confluence.source import ConfluenceSource

router = APIRouter()


@router.post("/load-knowledge/confluence")
async def load_knowledge_from_confluence(request: ConfluenceOptions):
    confluence_source = ConfluenceSource(request)
    result = confluence_source.process()
    return result
