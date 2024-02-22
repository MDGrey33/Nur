# ./api/endpoint.py
import os
import logging
from fastapi import FastAPI
import uvicorn
from openai import OpenAI
import threading
from credentials import oai_api_key
from slack.event_consumer import process_question, process_feedback
from pydantic import BaseModel
from vector.chroma_threads import generate_embedding
from database.nur_database import add_or_update_embed_vector
from configuration import api_host, api_port

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

# refactor: probably should not be in the endpoint module.
def vectorize_document_and_store_in_db(page_id):
    """
    Vectorize a document and store it in the database.
    :param page_id: The ID of the page to vectorize.
    :return: None
    """
    embedding, error_message = generate_embedding(page_id)
    if embedding:
        # Store the embedding in the database
        add_or_update_embed_vector(page_id, embedding)
        logging.info(f"Embedding for page ID {page_id} stored in the database.")
    else:
        logging.error(f"Embedding for page ID {page_id} could not be generated. {error_message}")


@processor.post("/api/v1/questions")
def create_question(question_event: QuestionEvent):
    thread = threading.Thread(target=process_question, args=(question_event,))
    thread.start()
    return {"message": "Question received, processing in background", "data": question_event}


@processor.post("/api/v1/feedback")
def create_feedback(feedback_event: FeedbackEvent):  # Changed to handle feedback
    # Assuming you have a separate or modified process for handling feedback
    thread = threading.Thread(target=process_feedback,
                              args=(feedback_event,))  # You may need a different function for processing feedback
    thread.start()
    return {"message": "Feedback received, processing in background", "data": feedback_event}


@processor.post("/api/v1/embeds")
def create_embeds(EmbedRequest: EmbedRequest):
    """
    Endpoint to initiate the embedding generation and storage process in the background.
    """
    # Using threading to process the embedding generation and storage without blocking the endpoint response
    page_id = EmbedRequest.page_id
    thread = threading.Thread(target=vectorize_document_and_store_in_db, args=(page_id,))
    thread.start()
    return {"message": "Embedding generation initiated, processing in background", "page_id": page_id}


def main():
    """Entry point for starting the FastAPI application."""
    uvicorn.run("api.endpoint:processor", host=host, port=int(port), reload=True)


if __name__ == "__main__":
    main()
