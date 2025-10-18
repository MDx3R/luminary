from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.add_source_to_folder_use_case import (
    AddSourceToFolderCommand,
    IAddSourceToFolderUseCase,
)
from luminary.source.application.interfaces.respositories.source_repository import (
    ISourceRepository,
)


class AddSourceToFolderUseCase(IAddSourceToFolderUseCase):
    def __init__(
        self,
        folder_repository: IFolderRepository,
        source_repository: ISourceRepository,
    ) -> None:
        self.folder_repository = folder_repository
        self.source_repository = source_repository

    async def execute(self, command: AddSourceToFolderCommand) -> None:
        source = await self.source_repository.get_by_id(command.source_id)
        folder = await self.folder_repository.get_by_id(command.folder_id)

        if source.user_id != command.user_id or folder.user_id != command.user_id:
            # TODO: Custom exc, permission policy
            raise PermissionError

        folder.add_source(command.source_id)

        await self.folder_repository.save(folder)
