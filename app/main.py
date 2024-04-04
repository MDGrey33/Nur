from fastapi import FastAPI

from app.database.database import Base, engine

# Knowledge source
from app.knowledge_sources.routing import knowledge_sources_router

# Events source
from app.events.routing import events


app = FastAPI()


app.include_router(knowledge_sources_router.router)
app.include_router(events.router)
