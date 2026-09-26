"""Query use case: list folders for a user."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from luminary.folder.application.dtos.read_models import FolderSummaryReadModel


@dataclass(frozen=True)
class ListUserFoldersQuery:
    user_id: UUID


class IListUserFoldersUseCase(ABC):
    @abstractmethod
    async def execute(
        self, query: ListUserFoldersQuery
    ) -> Sequence[FolderSummaryReadModel]:
        """Return all folders owned by the user."""
        ...
