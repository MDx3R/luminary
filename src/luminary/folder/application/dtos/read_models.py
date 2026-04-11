"""Read models for Folder bounded context (query side)."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class FolderSourceItem:
    """Source item embedded in folder read model."""

    id: UUID
    title: str
    type: str
    fetch_status: str
    url: str | None = None
    file_id: UUID | None = None
    editable: bool | None = None


@dataclass(frozen=True)
class FolderChatItem:
    """Chat item embedded in folder read model."""

    id: UUID
    name: str
    model_id: UUID
    created_at: datetime


@dataclass(frozen=True)
class FolderEditorItem:
    """Editor snapshot in folder read model."""

    text: str
    updated_at: datetime


@dataclass(frozen=True)
class FolderReadModel:
    """Read projection for a single folder (detail)."""

    id: UUID
    name: str
    description: str | None
    assistant_id: UUID | None
    assistant_name: str | None
    editor: FolderEditorItem | None
    chats: Sequence[FolderChatItem]
    sources: Sequence[FolderSourceItem]
    created_at: datetime


@dataclass(frozen=True)
class FolderSummaryReadModel:
    """Read projection for folder list item."""

    id: UUID
    name: str
    description: str | None
    created_at: datetime
