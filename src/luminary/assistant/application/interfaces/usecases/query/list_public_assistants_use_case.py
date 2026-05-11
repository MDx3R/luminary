"""Query use case: list all public assistants with pagination."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field

from luminary.assistant.application.dtos.read_models import AssistantSummaryReadModel


@dataclass(frozen=True)
class ListPublicAssistantsQuery:
    offset: int = field(default=0)
    limit: int = field(default=20)


class IListPublicAssistantsUseCase(ABC):
    @abstractmethod
    async def execute(
        self, query: ListPublicAssistantsQuery
    ) -> Sequence[AssistantSummaryReadModel]:
        """Return all active PUBLIC assistants ordered by created_at DESC."""
        ...
