"""HTTP response DTOs for Assistant."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from luminary.assistant.application.dtos.read_models import (
    AssistantReadModel,
    AssistantSummaryReadModel,
)


class AssistantSummaryResponse(BaseModel):
    """Response for assistant list item."""

    id: UUID
    name: str
    description: str
    type: str

    @classmethod
    def from_read_model(
        cls, model: AssistantSummaryReadModel
    ) -> "AssistantSummaryResponse":
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            type=model.type,
        )


class AssistantResponse(BaseModel):
    """Response for a single assistant (GET /assistants/{id})."""

    id: UUID
    name: str
    description: str
    type: str
    prompt: str
    created_at: datetime

    @classmethod
    def from_read_model(cls, model: AssistantReadModel) -> "AssistantResponse":
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            type=model.type,
            prompt=model.prompt,
            created_at=model.created_at,
        )
