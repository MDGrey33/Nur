import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CONFLUENCE_TEST_URL: str
    CONFLUENCE_TEST_USERNAME: str
    CONFLUENCE_TEST_API_TOKEN: str

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "./.env")


@lru_cache
def get_settings():
    return Settings()
