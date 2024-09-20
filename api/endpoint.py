# ./api/endpoint.py
import os
import logging
from fastapi import FastAPI
import uvicorn
from openai import OpenAI
import threading
from credentials import oai_api_key  # Import the API key from credentials
from slack.event_consumer import process_question, process_feedback
from pydantic import BaseModel
from vector.chroma import vectorize_document_and_store_in_db
from configuration import api_host, api_port
from interactions.vectorize_and_store import vectorize_interaction_and_store_in_db
from trivia.trivia_manager import TriviaQuizz

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

host = os.environ.get("NUR_API_HOST", api_host)
port = os.environ.get("NUR_API_PORT", api_port)

processor = FastAPI()

client = OpenAI(api_key=oai_api_key)

BASE_URL = "https://api.openai.com/v2"

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


@processor.post("/api/v1/questions")
def create_question(question_event: QuestionEvent):
    try:
        response = client.create_assistant(
            instructions="Answer the question based on the provided context.",
            model="text-davinci-003",
            tools=["retrieval"],
            input=question_event.text
        )
        return {
            "message": "Question received, processing in background",
            "data": response,
        }
    except openai.error.OpenAIError as e:
        logger.error(f"Error querying OpenAI API: {e}")
        return {"error": "Failed to process the question"}


@processor.post("/api/v1/feedback")
def create_feedback(feedback_event: FeedbackEvent):
    thread = threading.Thread(target=process_feedback, args=(feedback_event,))
    thread.start()
    return {
        "message": "Feedback received, processing in background",
        "data": feedback_event,
    }


@processor.post("/api/v1/embeds")
def create_embeds(embed_request: EmbedRequest):
    page_id = embed_request.page_id
    thread = threading.Thread(
        target=vectorize_document_and_store_in_db, args=(page_id,)
    )
    thread.start()
    return {
        "message": "Embedding generation initiated, processing in background",
        "page_id": page_id,
    }


@processor.post("/api/v1/interaction_embeds")
def create_interaction_embeds(interaction_embed_request: InteractionEmbedRequest):
    interaction_id = interaction_embed_request.interaction_id
    print(f"Received interaction embed request for ID: {interaction_id}")

    thread = threading.Thread(
        target=vectorize_interaction_and_store_in_db, args=(interaction_id,)
    )
    thread.start()

    return {
        "message": "Interaction embedding generation initiated, processing in background",
        "interaction_id": interaction_id,
    }


@processor.post("/api/v1/create_trivia")
def create_trivia(trivia_request_event: TriviaRequestEvent):
    thread = threading.Thread(target=TriviaQuizz, args=(trivia_request_event,))
    thread.start()
    return {
        "message": "Trivia creation request initiated, processing in background",
        "data": trivia_request_event,
    }


def main():
    """Entry point for starting the FastAPI application."""
    uvicorn.run("api.endpoint:processor", host=host, port=int(port), reload=True)


if __name__ == "__main__":
    main()
