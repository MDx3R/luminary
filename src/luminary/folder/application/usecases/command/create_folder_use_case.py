from uuid import UUID

from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.create_folder_use_case import (
    CreateFolderCommand,
    ICreateFolderUseCase,
)
from luminary.folder.domain.interfaces.folder_factory import (
    IFolderFactory,
)


class CreateFolderUseCase(ICreateFolderUseCase):
    def __init__(
        self, folder_factory: IFolderFactory, folder_repository: IFolderRepository
    ) -> None:
        self.folder_factory = folder_factory
        self.folder_repository = folder_repository

    async def execute(self, command: CreateFolderCommand) -> UUID:
        folder = self.folder_factory.create(
            command.name,
            command.description,
            command.user_id,
            command.model_id,
            command.assistant_id,
        )

        await self.folder_repository.add(folder)

        return folder.folder_id
