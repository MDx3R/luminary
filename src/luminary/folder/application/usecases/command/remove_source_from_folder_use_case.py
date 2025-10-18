from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.remove_source_from_folder_use_case import (
    IRemoveSourceFromFolderUseCase,
    RemoveSourceFromFolderCommand,
)


class RemoveSourceFromFolderUseCase(IRemoveSourceFromFolderUseCase):
    def __init__(self, folder_repository: IFolderRepository) -> None:
        self.folder_repository = folder_repository

    async def execute(self, command: RemoveSourceFromFolderCommand) -> None:
        folder = await self.folder_repository.get_by_id(command.folder_id)

        if folder.user_id != command.user_id:
            raise PermissionError

        if not folder.has_file(command.source_id):
            return

        folder.remove_file(command.source_id)
        await self.folder_repository.save(folder)
