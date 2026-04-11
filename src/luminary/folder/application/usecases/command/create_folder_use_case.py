from uuid import UUID

from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.create_folder_use_case import (
    CreateFolderCommand,
    ICreateFolderUseCase,
)
from luminary.folder.domain.interfaces.folder_factory import IFolderFactory


class CreateFolderUseCase(ICreateFolderUseCase):
    def __init__(
        self,
        folder_factory: IFolderFactory,
        folder_repository: IFolderRepository,
    ) -> None:
        self.folder_factory = folder_factory
        self.folder_repository = folder_repository

    async def execute(self, command: CreateFolderCommand) -> UUID:
        assistant_id = (
            AssistantId(command.assistant_id) if command.assistant_id else None
        )
        folder = self.folder_factory.create(
            name=command.name,
            description=command.description,
            user_id=UserId(command.user_id),
            assistant_id=assistant_id,
        )
        await self.folder_repository.add(folder)
        return folder.id.value
