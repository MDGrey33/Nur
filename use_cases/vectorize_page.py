import logging
from open_ai.embedding.embed_manager import embed_text
from configuration import embedding_model_id
from database.page_manager import add_or_update_embed_vector
from vector.chroma import upsert_page_to_chromadb

async def vectorize_and_store_page(page_id: str, title: str, body: str, metadata: dict):
    try:
        author = metadata.get("author", "Unknown")
        space_key = metadata.get("space_key") or metadata.get("spaceKey") or "Unknown"
        text = f"Author: {author}\nSpace Key: {space_key}\nTitle: {title}\n{body}"
        embedding = embed_text(text, embedding_model_id)
        add_or_update_embed_vector(page_id, embedding)
        upsert_page_to_chromadb(page_id)
        logging.info(f"Page {page_id} vectorized and stored in vector DB and Chroma.")
    except Exception as e:
        logging.error(f"Failed to vectorize/store page {page_id}: {e}") 