# /nurai/chat_services/routing/chat_service_router.py
from fastapi import APIRouter, HTTPException, Query, Depends
from nurai.chat_services.chat_service_factory import ChatServiceFactory
from nurai.chat_services.slack.slack_client import SlackClient
from nurai.logger.logger import setup_logger
from nurai.chat_services.chat_service_interface import ChatServiceInterface


logging = setup_logger()

router = APIRouter()

@router.post("/start-chat-service/")
async def start_chat_service(service_name: str = Query("slack", description="The name of the chat service to start.")):
    try:
        chat_service = ChatServiceFactory.get_service(service_name)
        chat_service.start_service()
        return {"message": f"{service_name} service started successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/fetch-chat-thread/")
async def fetch_chat_thread(service_name: str = Query(..., description="The name of the chat service."),
                            channel: str = Query(..., description="The ID of the channel."),
                            ts: str = Query(..., description="The thread timestamp.")):
    try:
        chat_service: ChatServiceInterface = ChatServiceFactory.get_service(service_name)
        messages = chat_service.fetch_thread_messages(channel=channel, thread_ts=ts)
        if messages is None:
            logging.error("No messages returned from fetch_thread_messages")
            raise HTTPException(status_code=404, detail="Messages could not be fetched.")
        interaction_input = chat_service.transform_messages_to_interaction_input(messages, channel)
        if interaction_input is None:
            logging.error("Failed to transform messages into interaction input.")
            raise HTTPException(status_code=404, detail="Failed to transform messages into interaction input.")
        logging.info("Successfully fetched and transformed thread")
        return interaction_input
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error fetching or transforming thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))

