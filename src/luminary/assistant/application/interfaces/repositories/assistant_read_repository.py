"""Read repository interface for Assistant query side."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from luminary.assistant.application.dtos.read_models import (
    AssistantReadModel,
    AssistantSummaryReadModel,
)


class IAssistantReadRepository(ABC):
    """Returns read models for assistant queries; access controlled via owner_id."""

    @abstractmethod
    async def get_by_id(self, assistant_id: UUID, owner_id: UUID) -> AssistantReadModel:
        """Return assistant read model or raise NotFoundError if not found or not owned."""
        ...

    @abstractmethod
    async def list_by_owner(
        self, owner_id: UUID
    ) -> Sequence[AssistantSummaryReadModel]:
        """Return all active assistants for the owner, ordered by created_at DESC."""
        ...
