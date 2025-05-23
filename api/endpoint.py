# ./api/endpoint.py
import os
from fastapi import FastAPI, BackgroundTasks
import uvicorn
from openai import OpenAI
import threading
from credentials import oai_api_key
from slack.event_consumer import process_question, process_feedback
from pydantic import BaseModel
from vector.chroma import vectorize_document_and_store_in_db
from configuration import api_host, api_port, system_confluence_knowledge_space
from interactions.vectorize_and_store import vectorize_interaction_and_store_in_db
from trivia.trivia_manager import TriviaQuizz
from use_cases.conversation_to_document import generate_document_from_conversation
from confluence_integration.system_knowledge_manager import create_page_on_confluence
from database.bookmarked_conversation_manager import BookmarkedConversationManager
from use_cases.vectorize_page import vectorize_and_store_page
from confluence_integration.confluence_client import ConfluenceClient
import httpx
import logging
from confluence_integration.store_page_local import store_page_locally_from_confluence

host = os.environ.get("NUR_API_HOST", api_host)
port = os.environ.get("NUR_API_PORT", api_port)

processor = FastAPI()

client = OpenAI(api_key=oai_api_key)


class QuestionEvent(BaseModel):
    text: str
    ts: str
    thread_ts: str
    channel: str
    user: str


class FeedbackEvent(BaseModel):
    text: str
    ts: str
    thread_ts: str
    channel: str
    user: str


class EmbedRequest(BaseModel):
    page_id: str


class InteractionEmbedRequest(BaseModel):
    interaction_id: str


class TriviaRequestEvent(BaseModel):
    domain: str
    thread_ts: str
    channel: str
    user: str


class NajmBookmarkEvent(BaseModel):
    conversation: str
    thread_id: str


@processor.post("/api/v1/questions")
def create_question(question_event: QuestionEvent):
    thread = threading.Thread(target=process_question, args=(question_event,))
    thread.start()
    return {
        "message": "Question received, processing in background",
        "data": question_event,
    }


@processor.post("/api/v1/feedback")
def create_feedback(feedback_event: FeedbackEvent):  # Changed to handle feedback
    # Assuming you have a separate or modified process for handling feedback
    thread = threading.Thread(
        target=process_feedback, args=(feedback_event,)
    )  # You may need a different function for processing feedback
    thread.start()
    return {
        "message": "Feedback received, processing in background",
        "data": feedback_event,
    }


# refactor: should be changed to page_embed
@processor.post("/api/v1/embeds")
def create_embeds(EmbedRequest: EmbedRequest):
    """
    Endpoint to initiate the embedding generation and storage process in the background.
    """
    # Using threading to process the embedding generation and storage without blocking the endpoint response
    page_id = EmbedRequest.page_id
    thread = threading.Thread(
        target=vectorize_document_and_store_in_db, args=(page_id,)
    )
    thread.start()
    return {
        "message": "Embedding generation initiated, processing in background",
        "page_id": page_id,
    }


@processor.post("/api/v1/interaction_embeds")
def create_interaction_embeds(InteractionEmbedRequest: InteractionEmbedRequest):
    """
    Endpoint to initiate the embedding generation and storage process in the background.
    """
    interaction_id = InteractionEmbedRequest.interaction_id
    print(
        f"Received interaction embed request for ID: {interaction_id}"
    )  # Debugging line

    # Use threading to process the embedding generation and storage without blocking the endpoint response
    thread = threading.Thread(
        target=vectorize_interaction_and_store_in_db, args=(interaction_id,)
    )
    thread.start()

    # Make sure to return a response that matches what your client expects
    return {
        "message": "Interaction embedding generation initiated, processing in background",
        "interaction_id": interaction_id,
    }


@processor.post("/api/v1/create_trivia")
def create_trivia(TriviaRequestEvent: TriviaRequestEvent):
    """
    Endpoint to initiate a trivia quizz based on a sepecific domain and share it in specified channel.
    args: domain, thread_ts, channel, user
    """
    # Using retrieve context retrieve interactions where the model failed to find relevant context that are closest to the domain mentioned.
    # Share the questions on the channel in question and tag the user.
    # The bot then posts the first question and allows the conversation to go on untill it detects a :check mark: emoji on each question.
    # The bot will also count the thumbs up provided on each message and keep track of each users thumbs up count.
    # The bot then creates a confluence page under "Q&A KB" confluence space tagging the top 3 contributors

    thread = threading.Thread(target=TriviaQuizz, args=(TriviaRequestEvent))
    thread.start()
    return "STUB TEXT - STILL IN DEVELOPMENT \nmessage: Trivia creation request initiated, processing in background"


@processor.post("/api/v1/bookmark_to_confluence")
def bookmark_to_confluence(event: NajmBookmarkEvent, background_tasks: BackgroundTasks):
    doc = generate_document_from_conversation(event.conversation)
    title = doc["title"]
    body = doc["body"]
    bookmarked_conversation_manager = BookmarkedConversationManager()
    bookmarked_conversation_manager.add_bookmarked_conversation(
        title=title, body=body, thread_id=event.thread_id
    )
    create_page_on_confluence(title, body)
    bookmarked_conversation_manager.update_posted_on_confluence(event.thread_id)
    # Retrieve page_id from Confluence
    confluence_client = ConfluenceClient()
    space_key = confluence_client.create_space_if_not_found(system_confluence_knowledge_space)
    page_id = confluence_client.get_page_id_by_title(space_key, title)

    # Store the page locally and in the DB before embedding
    try:
        store_page_locally_from_confluence(page_id, space_key)
    except Exception as e:
        logging.error(f"Failed to store page {page_id} locally or in DB: {e}")
        return {"error": f"Failed to store page locally: {e}"}

    # Add vectorization as a background task (new logic)
    try:
        background_tasks.add_task(vectorize_and_store_page, page_id, title, body, {})
        logging.info(f"Vectorization task for page {page_id} scheduled.")
    except Exception as e:
        logging.error(f"Failed to schedule vectorization task for page {page_id}: {e}")

    return {"message": "Bookmark event received, processing in background", "thread_id": event.thread_id}


def main():
    """Entry point for starting the FastAPI application."""
    uvicorn.run("api.endpoint:processor", host=host, port=int(port), reload=True)


if __name__ == "__main__":
    main()
