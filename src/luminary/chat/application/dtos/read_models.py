"""Read models for Chat bounded context (query side)."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ChatSourceItem:
    """Source item embedded in chat read model."""

    id: UUID
    title: str
    type: str
    fetch_status: str
    url: str | None = None
    file_id: UUID | None = None
    editable: bool | None = None


@dataclass(frozen=True)
class ChatReadModel:
    """Read projection for a single chat (detail)."""

    id: UUID
    name: str
    folder_id: UUID | None
    assistant_id: UUID | None
    assistant_name: str | None
    model_id: UUID
    max_context_messages: int
    sources: Sequence[ChatSourceItem]
    created_at: datetime


@dataclass(frozen=True)
class ChatSummaryReadModel:
    """Read projection for chat list item."""

    id: UUID
    name: str
    model_id: UUID
    created_at: datetime


@dataclass(frozen=True)
class AttachmentReadModel:
    """Attachment in a message."""

    name: str
    content_id: UUID
    source_id: UUID | None


@dataclass(frozen=True)
class MessageReadModel:
    """Read projection for a message."""

    id: UUID
    chat_id: UUID
    role: str
    status: str
    content: str
    model_id: UUID
    tokens: int | None
    created_at: datetime
    edited_at: datetime
    attachments: Sequence[AttachmentReadModel]
