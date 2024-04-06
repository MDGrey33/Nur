from fastapi import FastAPI


# Knowledge source
from app.knowledge_sources.routing import knowledge_sources_router

# Events source
from app.events.routing import events

# Assistants
from app.assistants.routing import assistants_router

# Slack Bot
from app.chat_services.routing import chat_service_router


app = FastAPI()


app.include_router(knowledge_sources_router.router)
app.include_router(events.router)
app.include_router(assistants_router.router)
app.include_router(chat_service_router.router)