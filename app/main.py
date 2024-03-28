
from fastapi import FastAPI

from app.database.database import Base, engine
# Knowledge source
from app.knowledge_sources.routing import knowledge_sources_router

app = FastAPI()

Base.metadata.create_all(bind=engine)


app.include_router(knowledge_sources_router.router)
