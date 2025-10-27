from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CreateSourceDTO:
    user_id: UUID
    name: str


@dataclass(frozen=True)
class UpdateSourceDTO:
    source_id: UUID
    name: str


@dataclass(frozen=True)
class DeleteSourceDTO:
    source_id: UUID


@dataclass(frozen=True)
class SourceDTO:
    source_id: UUID
    user_id: UUID
    name: str
    created_at: datetime
