"""HTTP response DTOs for Folder."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from luminary.folder.application.dtos.read_models import (
    FolderChatItem,
    FolderEditorItem,
    FolderReadModel,
    FolderSourceItem,
    FolderSummaryReadModel,
)


class FolderSourceItemResponse(BaseModel):
    id: UUID
    title: str
    type: str
    fetch_status: str
    url: str | None
    file_id: UUID | None
    editable: bool | None

    @classmethod
    def from_read_model(cls, model: FolderSourceItem) -> "FolderSourceItemResponse":
        return cls(
            id=model.id,
            title=model.title,
            type=model.type,
            fetch_status=model.fetch_status,
            url=model.url,
            file_id=model.file_id,
            editable=model.editable,
        )


class FolderChatItemResponse(BaseModel):
    id: UUID
    name: str
    model_id: UUID
    created_at: datetime

    @classmethod
    def from_read_model(cls, model: FolderChatItem) -> "FolderChatItemResponse":
        return cls(
            id=model.id,
            name=model.name,
            model_id=model.model_id,
            created_at=model.created_at,
        )


class FolderEditorItemResponse(BaseModel):
    text: str
    updated_at: datetime

    @classmethod
    def from_read_model(cls, model: FolderEditorItem) -> "FolderEditorItemResponse":
        return cls(
            text=model.text,
            updated_at=model.updated_at,
        )


class FolderResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    assistant_id: UUID | None
    assistant_name: str | None
    editor: FolderEditorItemResponse | None
    chats: list[FolderChatItemResponse]
    sources: list[FolderSourceItemResponse]
    created_at: datetime

    @classmethod
    def from_read_model(cls, model: FolderReadModel) -> "FolderResponse":
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            assistant_id=model.assistant_id,
            assistant_name=model.assistant_name,
            editor=(
                FolderEditorItemResponse.from_read_model(model.editor)
                if model.editor
                else None
            ),
            chats=[FolderChatItemResponse.from_read_model(c) for c in model.chats],
            sources=[
                FolderSourceItemResponse.from_read_model(s) for s in model.sources
            ],
            created_at=model.created_at,
        )


class FolderSummaryResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_at: datetime

    @classmethod
    def from_read_model(cls, model: FolderSummaryReadModel) -> "FolderSummaryResponse":
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )
