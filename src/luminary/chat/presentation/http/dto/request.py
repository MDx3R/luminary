from uuid import UUID

from pydantic import BaseModel


class CreateChatRequest(BaseModel):
    name: str | None = None
    assistant_id: UUID | None = None


class UpdateChatNameRequest(BaseModel):
    name: str


class MoveChatRequest(BaseModel):
    folder_id: UUID | None


class ReorderChatsRequest(BaseModel):
    chat_id: UUID
    previous_chat_id: UUID | None = None
    next_chat_id: UUID | None = None


class ChangeChatAssistantRequest(BaseModel):
    assistant_id: UUID


class AddSourceToChatRequest(BaseModel):
    source_id: UUID


class SendMessageRequest(BaseModel):
    content: str
