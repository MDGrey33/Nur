# ./gpt_4t/format_knowledge_gathering.py
from openai import OpenAI
from credentials import oai_api_key
from configuration import file_system_path
from configuration import model_id

client = OpenAI(api_key=oai_api_key)


def get_response_from_gpt_4t(question, context):
    """
    Queries the GPT-4T model with a specific question and context.

    Args:
    question (str): The question to be asked.
    context (str): The context to be used for answering the question.

    Returns:
    str: The response from the GPT-4T model.
    """
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "system",
                    "content": "You are the expert on formatting Q&A conversation into a confluence page content.\n"
                    "You will always review and refer to the information included as context. \n"
                    "You will review the initial question and format it as a title.\n"
                    "you will review the full conversation and format the information relevant to the question as a confluence page content "
                    "The new confluence page you are making should be used in the future to answer the question in the title.\n"
                    "You will exclude information mentioned that is not relevant for the context.\n"
                    "Knowing its a human conversation there might be jokes, notice them and dont mention them if they do not relate to the scope of the question.\n"
                    "You will never improvise or create content from outside the context.\n"
                    "If you do not have the answer based on the context you will return an empty json.\n"
                    "You will provide the response in json format containing page title, and page content.\n"
                    "You will strictly use the following formats for the empty json: \n"
                    "{'page_title': '', 'page_content': ''}\n"
                    "you will strictly use the following formats for the json with content: \n"
                    "{'page_title': 'The title of the confluence page', 'page_content': 'The content of the confluence page'}",
                },
                {
                    "role": "user",
                    "content": f"find here the conversation in context format it into a confluence page json conversation:{context}",
                },
            ],
            temperature=0,
            max_tokens=4095,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
    except Exception as e:
        print(f"Error querying GPT-4T: {e}")
        return None
    if response:
        answer = response.choices[0].message.content
        return answer
    else:
        return None


def query_gpt_4t_with_context(_, context):
    response = get_response_from_gpt_4t(_, context)
    return response
