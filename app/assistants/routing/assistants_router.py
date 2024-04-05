from fastapi import APIRouter, Depends, BackgroundTasks

from app.assistants.controllers.assistant_create_controller import AssistantCreateController
from app.assistants.requests.assistant_create_request import AssistantCreateRequest
from app.database.database import get_db

router = APIRouter()


@router.post('/assistants/create')
async def manage_assistant(request: AssistantCreateRequest, db=Depends(get_db)):
    controller = AssistantCreateController(db)
    response = controller.process(request)

    return response
