from functools import lru_cache

import openai
from fastapi import APIRouter, Depends

from app.knowledge_sources.confluence.requests.confluence_options import ConfluenceOptions
from app.knowledge_sources.confluence.source import ConfluenceSource
from app.knowledge_sources.settings import get_settings

router = APIRouter()

settings = get_settings()


@lru_cache
def get_open_ai_client():
    return openai.OpenAI(api_key=settings.OPEN_AI_KEY)


@router.post('/load-knowledge/confluence')
async def load_knowledge_from_confluence(request: ConfluenceOptions, open_ai_client=Depends(get_open_ai_client)):
    confluence_source = ConfluenceSource(request, open_ai_client)
    result = confluence_source.process()
    return result
