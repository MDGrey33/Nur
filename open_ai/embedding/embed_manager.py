import openai
from credentials import oai_api_key
from configuration import embedding_model_id

client = openai.OpenAI(api_key=oai_api_key)


def embed_text(text, model):
    response = client.embeddings.create(input=text, model=model)
    embedding = response.data[0].embedding
    return embedding

