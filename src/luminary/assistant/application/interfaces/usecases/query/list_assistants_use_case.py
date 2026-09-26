"""Query use case: list assistants visible to a user."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from luminary.assistant.application.dtos.read_models import AssistantSummaryReadModel


@dataclass(frozen=True)
class ListUserAssistantsQuery:
    user_id: UUID


class IListUserAssistantsUseCase(ABC):
    @abstractmethod
    async def execute(
        self, query: ListUserAssistantsQuery
    ) -> Sequence[AssistantSummaryReadModel]:
        """Return PERSONAL (owned) + all SYSTEM + PUBLIC (owned) assistants."""
        ...
