from fastapi import FastAPI

# Knowledge source
from nurai.knowledge_sources.routing import knowledge_sources_router

# Events source
from nurai.events.routing import events

# Assistants
from nurai.assistants.routing import assistants_router

# Slack Bot
from nurai.chat_services.routing import chat_service_router

# Interactions
from nurai.interactions.routing.interaction_service_router import (
    router as interactions_router,
)

app = FastAPI()

app.include_router(knowledge_sources_router.router)
app.include_router(events.router)
app.include_router(assistants_router.router)
app.include_router(chat_service_router.router)
app.include_router(interactions_router)
