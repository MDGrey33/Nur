from pydantic import BaseModel


class ConfluenceOptions(BaseModel):
    base_url: str
    username: str
    access_token: str
    space_name: str
    space_key: str
