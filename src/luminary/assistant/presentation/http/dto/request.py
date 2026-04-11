from pydantic import BaseModel


class CreateAssistantRequest(BaseModel):
    name: str
    description: str
    prompt: str | None = None


class UpdateAssistantInfoRequest(BaseModel):
    name: str
    description: str


class UpdateAssistantInstructionsRequest(BaseModel):
    prompt: str
