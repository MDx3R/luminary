from pydantic import BaseModel


class CreateAssistantRequest(BaseModel):
    name: str
    description: str
    prompt: str | None
