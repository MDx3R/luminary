"""Query use case: list sources for a user."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from luminary.source.application.dtos.read_models import SourceReadModel


@dataclass(frozen=True)
class ListUserSourcesQuery:
    user_id: UUID


class IListUserSourcesUseCase(ABC):
    @abstractmethod
    async def execute(self, query: ListUserSourcesQuery) -> Sequence[SourceReadModel]:
        """Return all sources owned by the user."""
        ...
