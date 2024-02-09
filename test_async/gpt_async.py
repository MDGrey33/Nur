import asyncio
from functools import wraps, partial
from openai import OpenAI
from credentials import oai_api_key
from configuration import model_id

client = OpenAI(api_key=oai_api_key)


# Define an async wrapper function to run sync code in a separate thread
def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run


# Correctly apply async_wrap to the OpenAI client method
async_client_chat_completions_create = async_wrap(client.chat.completions.create)


async def get_response_from_gpt_4t(question, context=""):
    response = await async_client_chat_completions_create(
        model=model_id,
        messages=[
            {"role": "system", "content": "do it fast"},
            {"role": "user", "content": f"question: {question}\npages:{context}"}
        ],
        temperature=0,
        max_tokens=4095,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    answer = response.choices[0].message.content
    return answer


async def main():
    questions = ["who is the president of the united states?",
                 "who is the president of the united kingdom?",
                 "who is the president of france?",
                 "who is the president of germany?",
                 "who is the president of italy?",
                 "who is the president of spain?"]

    tasks = [get_response_from_gpt_4t(question) for question in questions]
    responses = await asyncio.gather(*tasks)
    for question, response in zip(questions, responses):
        print(f"Question: {question}\nAnswer: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())
