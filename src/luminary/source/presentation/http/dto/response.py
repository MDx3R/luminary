"""HTTP response DTOs for Source."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from luminary.source.application.dtos.read_models import SourceReadModel


class SourceResponse(BaseModel):
    """Response for a single source (GET /sources/{id} or list item)."""

    id: UUID
    title: str
    type: str
    fetch_status: str
    created_at: datetime
    url: str | None = None
    file_id: UUID | None = None
    editable: bool | None = None

    @classmethod
    def from_read_model(cls, model: SourceReadModel) -> "SourceResponse":
        return cls(
            id=model.id,
            title=model.title,
            type=model.type,
            fetch_status=model.fetch_status,
            created_at=model.created_at,
            url=model.url,
            file_id=model.file_id,
            editable=model.editable,
        )
