"""Query use case: get folder by id."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from luminary.folder.application.dtos.read_models import FolderReadModel


@dataclass(frozen=True)
class GetFolderByIdQuery:
    user_id: UUID
    folder_id: UUID


class IGetFolderByIdUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetFolderByIdQuery) -> FolderReadModel:
        """Return folder read model for the given id and owner."""
        ...
