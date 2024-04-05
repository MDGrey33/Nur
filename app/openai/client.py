from functools import lru_cache
from app.settings.settings import get_settings

import openai

settings = get_settings()

@lru_cache
def get_open_ai_client():
    return openai.OpenAI(api_key=settings.OPEN_AI_KEY)