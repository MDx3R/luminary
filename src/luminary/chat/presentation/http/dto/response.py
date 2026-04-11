from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from luminary.chat.application.dtos.read_models import (
    ChatReadModel,
    ChatSourceItem,
    ChatSummaryReadModel,
    MessageReadModel,
)
from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    StreamingMessageDTO,
    StreamState,
)
from luminary.chat.domain.enums import Author, MessageStatus


class ChatSourceItemResponse(BaseModel):
    id: UUID
    title: str
    type: str
    fetch_status: str
    url: str | None
    file_id: UUID | None
    editable: bool | None

    @classmethod
    def from_read_model(cls, model: ChatSourceItem) -> "ChatSourceItemResponse":
        return cls(
            id=model.id,
            title=model.title,
            type=model.type,
            fetch_status=model.fetch_status,
            url=model.url,
            file_id=model.file_id,
            editable=model.editable,
        )


class ChatResponse(BaseModel):
    id: UUID
    name: str
    folder_id: UUID | None
    assistant_id: UUID | None
    assistant_name: str | None
    model_id: UUID
    max_context_messages: int
    sources: list[ChatSourceItemResponse]
    created_at: datetime

    @classmethod
    def from_read_model(cls, model: ChatReadModel) -> "ChatResponse":
        return cls(
            id=model.id,
            name=model.name,
            folder_id=model.folder_id,
            assistant_id=model.assistant_id,
            assistant_name=model.assistant_name,
            model_id=model.model_id,
            max_context_messages=model.max_context_messages,
            sources=[ChatSourceItemResponse.from_read_model(s) for s in model.sources],
            created_at=model.created_at,
        )


class ChatSummaryResponse(BaseModel):
    id: UUID
    name: str
    model_id: UUID
    created_at: datetime

    @classmethod
    def from_read_model(cls, model: ChatSummaryReadModel) -> "ChatSummaryResponse":
        return cls(
            id=model.id,
            name=model.name,
            model_id=model.model_id,
            created_at=model.created_at,
        )


class AttachmentResponse(BaseModel):
    name: str
    content_id: UUID
    source_id: UUID | None


class MessageResponse(BaseModel):
    id: UUID
    chat_id: UUID
    role: str
    status: str
    content: str
    model_id: UUID
    tokens: int | None
    created_at: datetime
    edited_at: datetime
    attachments: list[AttachmentResponse]

    @classmethod
    def from_read_model(cls, model: MessageReadModel) -> "MessageResponse":
        return cls(
            id=model.id,
            chat_id=model.chat_id,
            role=model.role,
            status=model.status,
            content=model.content,
            model_id=model.model_id,
            tokens=model.tokens,
            created_at=model.created_at,
            edited_at=model.edited_at,
            attachments=[
                AttachmentResponse(
                    name=a.name,
                    content_id=a.content_id,
                    source_id=a.source_id,
                )
                for a in model.attachments
            ],
        )


class StreamingMessageResponse(BaseModel):
    message_id: UUID
    state: StreamState
    content: str
    author: Author
    status: MessageStatus

    @classmethod
    def from_dto(cls, dto: StreamingMessageDTO) -> Self:
        return cls(
            message_id=dto.message_id,
            state=dto.state,
            content=dto.content,
            author=dto.author,
            status=dto.status,
        )
