from fastapi import FastAPI
import uvicorn
from openai import OpenAI
import threading
from credentials import oai_api_key
from slack.event_consumer import process_question, process_feedback
from pydantic import BaseModel

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

'''
def get_response_from_gpt_4t(question, context=""):
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are the Q&A assistant.\n"},
            {"role": "user", "content": f"question: {question}\npages:{context}"}
        ],
        temperature=0,
        max_tokens=4095,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    answer = response.choices[0].message.content.strip()
    return answer


def process_question(question_event: QuestionEvent):
    answer = get_response_from_gpt_4t(question_event.text)
    print(f"question processed by the api {answer}")


def process_feedback(question_event: QuestionEvent):
    answer = get_response_from_gpt_4t(question_event.text)
    print(f"feedback processed by the api {answer}")
'''


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


def main():
    """Entry point for starting the FastAPI application."""
    uvicorn.run("api.endpoint:processor", host="localhost", port=8000, reload=True)


if __name__ == "__main__":
    main()
