import logging
from configuration import EMBEDDING_MODEL_MAX_TOKENS

# Estimate: 4 characters per token (OpenAI guidance)
CHARS_PER_TOKEN = 4

def should_skip_embedding(page_content: str, model: str) -> bool:
    """
    Returns True if the page is too large to embed for the given model.
    """
    max_tokens = EMBEDDING_MODEL_MAX_TOKENS.get(model, 8192)  # Default to 8192 if unknown
    max_chars = max_tokens * CHARS_PER_TOKEN
    if len(page_content) > max_chars:
        logging.warning(f"Skipping embedding: content length {len(page_content)} exceeds model limit ({max_chars} chars for {model})")
        return True
    return False 