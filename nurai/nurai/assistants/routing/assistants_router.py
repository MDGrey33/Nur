from fastapi import APIRouter, Depends, BackgroundTasks

from nurai.assistants.controllers.assistant_create_controller import (
    AssistantCreateController,
)
from nurai.assistants.requests.assistant_create_request import AssistantCreateRequest
from nurai.database.database import get_db

router = APIRouter()


@router.post("/assistants/create")
async def manage_assistant(request: AssistantCreateRequest, db=Depends(get_db)):
    controller = AssistantCreateController(db)
    response = controller.process(request)

    return response
