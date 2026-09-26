"""Query use case: get source by id."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from luminary.source.application.dtos.read_models import SourceReadModel


@dataclass(frozen=True)
class GetSourceByIdQuery:
    user_id: UUID
    source_id: UUID


class IGetSourceByIdUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetSourceByIdQuery) -> SourceReadModel:
        """Return source read model for the given id and owner."""
        ...
