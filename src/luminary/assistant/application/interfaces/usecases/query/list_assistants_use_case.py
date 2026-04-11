"""Query use case: list assistants for a user."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from luminary.assistant.application.dtos.read_models import AssistantSummaryReadModel


@dataclass(frozen=True)
class ListAssistantsQuery:
    user_id: UUID


class IListAssistantsUseCase(ABC):
    @abstractmethod
    async def execute(
        self, query: ListAssistantsQuery
    ) -> Sequence[AssistantSummaryReadModel]:
        """Return all assistants owned by the user."""
        ...
