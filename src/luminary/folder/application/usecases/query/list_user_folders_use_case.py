"""List user folders query use case implementation."""

from collections.abc import Sequence

from luminary.folder.application.dtos.read_models import FolderSummaryReadModel
from luminary.folder.application.interfaces.repositories.folder_read_repository import (
    IFolderReadRepository,
)
from luminary.folder.application.interfaces.usecases.query.list_user_folders_use_case import (
    IListUserFoldersUseCase,
    ListUserFoldersQuery,
)


class ListUserFoldersUseCase(IListUserFoldersUseCase):
    def __init__(self, read_repository: IFolderReadRepository) -> None:
        self._read_repository = read_repository

    async def execute(
        self, query: ListUserFoldersQuery
    ) -> Sequence[FolderSummaryReadModel]:
        return await self._read_repository.list_by_owner(query.user_id)
