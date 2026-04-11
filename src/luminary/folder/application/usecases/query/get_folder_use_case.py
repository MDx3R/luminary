"""Get folder by id query use case implementation."""

from luminary.folder.application.dtos.read_models import FolderReadModel
from luminary.folder.application.interfaces.repositories.folder_read_repository import (
    IFolderReadRepository,
)
from luminary.folder.application.interfaces.usecases.query.get_folder_use_case import (
    GetFolderByIdQuery,
    IGetFolderByIdUseCase,
)


class GetFolderByIdUseCase(IGetFolderByIdUseCase):
    def __init__(self, read_repository: IFolderReadRepository) -> None:
        self._read_repository = read_repository

    async def execute(self, query: GetFolderByIdQuery) -> FolderReadModel:
        return await self._read_repository.get_by_id(query.folder_id, query.user_id)
