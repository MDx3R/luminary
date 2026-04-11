"""Query use case: get assistant by id."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from luminary.assistant.application.dtos.read_models import AssistantReadModel


@dataclass(frozen=True)
class GetAssistantByIdQuery:
    user_id: UUID
    assistant_id: UUID


class IGetAssistantByIdUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetAssistantByIdQuery) -> AssistantReadModel:
        """Return assistant read model for the given id and owner."""
        ...
