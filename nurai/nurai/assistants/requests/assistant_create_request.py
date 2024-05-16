from typing import List

from pydantic import BaseModel


class AssistantCreateRequest(BaseModel):
    model: str
    name: str
    instructions: str
    tools: List[str]
    description: str
