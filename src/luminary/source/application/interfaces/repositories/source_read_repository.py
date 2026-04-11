"""Read repository interface for Source query side."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from luminary.source.application.dtos.read_models import SourceReadModel


class ISourceReadRepository(ABC):
    """Returns read models for source queries; access controlled via owner_id."""

    @abstractmethod
    async def get_by_id(self, source_id: UUID, owner_id: UUID) -> SourceReadModel:
        """Return source read model or raise NotFoundError if not found or not owned."""
        ...

    @abstractmethod
    async def list_by_owner(self, owner_id: UUID) -> Sequence[SourceReadModel]:
        """Return all active sources for the owner, ordered by created_at DESC."""
        ...
