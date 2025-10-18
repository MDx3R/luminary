from luminary.file.application.interfaces.respositories.file_repository import (
    IFileRepository,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.add_file_to_folder_use_case import (
    AddFileToFolderCommand,
    IAddFileToFolderUseCase,
)


class AddFileToFolderUseCase(IAddFileToFolderUseCase):
    def __init__(
        self,
        folder_repository: IFolderRepository,
        file_repository: IFileRepository,
    ) -> None:
        self.folder_repository = folder_repository
        self.file_repository = file_repository

    async def execute(self, command: AddFileToFolderCommand) -> None:
        file = await self.file_repository.get_by_id(command.file_id)
        folder = await self.folder_repository.get_by_id(command.folder_id)

        if file.user_id != command.user_id or folder.user_id != command.user_id:
            raise PermissionError

        folder.add_file(command.file_id)

        await self.folder_repository.save(folder)
