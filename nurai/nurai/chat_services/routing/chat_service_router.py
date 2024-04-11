# /nurai/chat_services/routing/chat_service_router.py
from fastapi import APIRouter, HTTPException, Query, Depends
from nurai.chat_services.chat_service_factory import ChatServiceFactory
from nurai.chat_services.slack.slack_client import SlackClient


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


@router.get("/fetch-slack-thread/")
async def fetch_slack_thread(channel: str = Query(..., description="The ID of the Slack channel."),
                             ts: str = Query(..., description="The thread timestamp."),
                             slack_client: SlackClient = Depends(SlackClient)):
    """
    Fetches a thread of messages from a specified Slack channel based on the thread timestamp and formats it for interaction input.
    """
    try:
        messages = slack_client.fetch_thread_messages(channel=channel, thread_ts=ts)
        if messages is None:
            raise HTTPException(status_code=404, detail="Messages could not be fetched.")
        # Transform messages to interaction input format
        interaction_input = slack_client.transform_messages_to_interaction_input(messages, channel)
        if interaction_input is None:
            raise HTTPException(status_code=404, detail="Failed to transform messages into interaction input.")
        return interaction_input
    except Exception as e:  # Consider catching more specific exceptions
        raise HTTPException(status_code=500, detail=str(e))
