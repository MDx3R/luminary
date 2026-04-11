from uuid import UUID

from pydantic import BaseModel


class CreateChatRequest(BaseModel):
    name: str | None = None
    assistant_id: UUID | None = None
    model_id: UUID
    max_context_messages: int


class UpdateChatNameRequest(BaseModel):
    name: str


class UpdateChatSettingsRequest(BaseModel):
    model_id: UUID
    max_context_messages: int


class ChangeChatAssistantRequest(BaseModel):
    assistant_id: UUID


class AddSourceToChatRequest(BaseModel):
    source_id: UUID


class SendMessageRequest(BaseModel):
    content: str
