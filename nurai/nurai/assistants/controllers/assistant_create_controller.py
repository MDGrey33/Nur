from nurai.assistants.models.assistant import Assistant
from nurai.assistants.requests.assistant_create_request import AssistantCreateRequest
from nurai.openai.client import get_open_ai_client


class AssistantCreateController:

    def __init__(self, db):
        self.open_ai_client = get_open_ai_client()
        self.db = db

    def process(self, request: AssistantCreateRequest):
        response = self.open_ai_client.beta.assistants.create(
            model=request.model,
            name=request.name,
            instructions=request.instructions,
            tools=request.tools,
            description=request.description,
        )

        assistant = Assistant(
            id=response.id,
            created_at=response.created_at,
            description=response.description,
            file_ids=response.file_ids,
            instructions=response.instructions,
            metadata=response.metadata,
            model=response.model,
            name=response.name,
            object=response.object,
            tools=response.tools,
        )

        assistant_row = assistant.get_or_create(self.db)

        return assistant_row
