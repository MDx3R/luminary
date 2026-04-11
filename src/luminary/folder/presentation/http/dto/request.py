from uuid import UUID

from pydantic import BaseModel


class CreateFolderRequest(BaseModel):
    name: str
    description: str | None = None
    assistant_id: UUID | None = None


class UpdateFolderInfoRequest(BaseModel):
    name: str
    description: str | None = None


class ChangeFolderAssistantRequest(BaseModel):
    assistant_id: UUID


class AddSourceToFolderRequest(BaseModel):
    source_id: UUID


class CreateFolderChatRequest(BaseModel):
    name: str | None = None
    assistant_id: UUID | None = None
    model_id: UUID
    max_context_messages: int


class UpdateEditorContentRequest(BaseModel):
    text: str
