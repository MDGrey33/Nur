# ./open_ai/embedding/embed_manager.py
import openai
import json
from credentials import oai_api_key

client = openai.OpenAI(api_key=oai_api_key)


def embed_text(text, model):
    """
    Embed the given text using the specified OpenAI model.
    :param text: The text to embed.
    :param model: The OpenAI model to use.
    :return: The embedding vector as a list of floats.
    """
    response = client.embeddings.create(input=text, model=model)
    embedding_vector = response.dict()["data"][0]["embedding"]
    return embedding_vector

