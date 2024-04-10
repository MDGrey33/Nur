# /nurai/chat_services/routing/chat_service_router.py
from fastapi import APIRouter, HTTPException, Query
from nurai.chat_services.chat_service_factory import ChatServiceFactory

router = APIRouter()


@router.post("/start-chat-service/")
async def start_chat_service(service_name: str = Query("slack", description="The name of the chat service to start. "
                                                                            "Currently, only 'slack' is supported.")):
    try:
        chat_service = ChatServiceFactory.get_service(service_name)
        chat_service.start_service()
        return {"message": f"{service_name} service started successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
