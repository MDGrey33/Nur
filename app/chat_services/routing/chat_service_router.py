from fastapi import APIRouter, HTTPException
from app.chat_services.chat_service_factory import ChatServiceFactory

router = APIRouter()


@router.post("/start-chat-service/{service_name}")
async def start_chat_service(service_name: str):
    try:
        chat_service = ChatServiceFactory.get_service(service_name)
        chat_service.start_service()
        return {"message": f"{service_name} service started successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
