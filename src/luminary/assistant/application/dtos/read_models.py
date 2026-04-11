"""Read models for Assistant bounded context (query side)."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class AssistantReadModel:
    """Read projection for a single assistant (detail)."""

    id: UUID
    name: str
    description: str
    type: str
    prompt: str
    created_at: datetime


@dataclass(frozen=True)
class AssistantSummaryReadModel:
    """Read projection for assistant list item."""

    id: UUID
    name: str
    description: str
    type: str
