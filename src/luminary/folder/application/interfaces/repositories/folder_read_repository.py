"""Read repository interface for Folder query side."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from luminary.folder.application.dtos.read_models import (
    FolderReadModel,
    FolderSummaryReadModel,
)


class IFolderReadRepository(ABC):
    """Returns read models for folder queries; access controlled via owner_id."""

    @abstractmethod
    async def get_by_id(self, folder_id: UUID, owner_id: UUID) -> FolderReadModel:
        """Return folder read model or raise NotFoundError if not found or not owned."""
        ...

    @abstractmethod
    async def list_by_owner(self, owner_id: UUID) -> Sequence[FolderSummaryReadModel]:
        """Return all active folders for the owner, ordered by created_at DESC."""
        ...
