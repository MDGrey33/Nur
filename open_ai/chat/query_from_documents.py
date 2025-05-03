# ./gpt_4t/query_from_documents_threads.py
from openai import OpenAI
from credentials import oai_api_key
from configuration import file_system_path, model_id, MODEL_MAX_TOKENS

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
                    "content": "You are the Q&A based on knowledge base assistant.\n"
                    "You will always review and refer to the pages included as context. \n"
                    "You will always answer from the pages.\n"
                    "You will never improvise or create content from outside the files.\n"
                    "If you do not have the answer based on the files you will clearly state that and abstain from answering.\n"
                    "If you use your knowledge to explain some information from outside the file, you will clearly state that.\n",
                },
                {
                    "role": "user",
                    "content": f"You will answer the following question with a summary, then provide a comprehensive answer, then provide the references aliasing them as Technical trace:  \nquestion: {question}\npages:{context}",
                },
            ],
            temperature=0,
            max_tokens=MODEL_MAX_TOKENS,
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


def format_pages_as_context(file_ids):
    """
    Adds specified files to the question's context for referencing in responses,
    including the document title and space key.

    Args:
    file_ids (list of str): List of file IDs to be added to the assistant.

    Returns:
    str: The formatted context.
    """
    context = None
    for file_id in file_ids:
        if not context:
            context = ""
        chosen_file_path = file_system_path + f"/{file_id}.txt"
        # Open file and extract title and space key
        try:
            with open(chosen_file_path, "r") as file:
                file_content = file.read()
                title = file_content.split("title: ")[1].split("\n")[0].strip()
                space_key = file_content.split("spaceKey: ")[1].split("\n")[0].strip()

                context += f"\nDocument Title: {title}\nSpace Key: {space_key}\n\n"
                context += file_content

            print(
                f"File {file_id} (Title: {title}, Space Key: {space_key}) appended to context successfully"
            )

        except Exception as e:
            print(f"Error appending file {file_id} to context: {e}")
    if context:
        return context
    else:
        return None


def query_gpt_4t_with_context(question, page_ids):
    """
    Queries the assistant with a specific question, after setting up the necessary context by adding relevant files.

    Args:
    question (str): The question to be asked.
    page_ids (list): A list of page IDs representing the files to be added to the assistant's context.

    Returns:
    list: A list of messages, including the assistant's response to the question.
    """
    # Format the context
    # Ensure page_ids is a list
    if not isinstance(page_ids, list):
        page_ids = [page_ids]
    context = format_pages_as_context(page_ids)
    # Query GPT-4T with the question and context
    response = get_response_from_gpt_4t(question, context)
    return response


if __name__ == "__main__":
    response = query_gpt_4t_with_context(
        "What do those documents talk about?", ["13795383", "24576050"]
    )
    print(response)
