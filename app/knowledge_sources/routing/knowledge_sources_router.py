from functools import lru_cache

import openai
from fastapi import APIRouter, Depends, BackgroundTasks

from app.database.database import get_db
from app.knowledge_sources.confluence.requests.confluence_options import ConfluenceOptions
from app.knowledge_sources.confluence.source import ConfluenceSource
from app.knowledge_sources.settings import get_settings
from app.tasks.models.task import Task

router = APIRouter()

settings = get_settings()


@lru_cache
def get_open_ai_client():
    return openai.OpenAI(api_key=settings.OPEN_AI_KEY)


def load_knowledge_from_confluence_background(request, open_ai_client, db):
    task = Task().get_or_create(db)
    task.status = Task.PROCESSING
    task.update(db)

    confluence_source = ConfluenceSource(request, open_ai_client, db, task.id)
    confluence_source.process()
@router.post('/load-knowledge/confluence')
async def load_knowledge_from_confluence(request: ConfluenceOptions, background_tasks: BackgroundTasks, open_ai_client=Depends(get_open_ai_client), db=Depends(get_db)):
    background_tasks.add_task(load_knowledge_from_confluence_background, request, open_ai_client, db)
    return {"message": "Processing started in the background"}
