from uuid import UUID

from pydantic import BaseModel


class CreateChatRequest(BaseModel):
    name: str | None = None
    assistant_id: UUID | None = None


class UpdateChatNameRequest(BaseModel):
    name: str


class ChangeChatAssistantRequest(BaseModel):
    assistant_id: UUID


class AddSourceToChatRequest(BaseModel):
    source_id: UUID


class SendMessageRequest(BaseModel):
    content: str
