"""Read models for Source bounded context (query side)."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class SourceReadModel:
    """Read projection for a single source."""

    id: UUID
    title: str
    type: str
    fetch_status: str
    created_at: datetime
    url: str | None = None  # link sources
    file_id: UUID | None = None  # file sources
    editable: bool | None = None  # page sources
