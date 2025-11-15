from uuid import UUID

from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assisnant import AssistantId
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
from luminary.model.domain.entity.model import ModelId


class CreateFolderUseCase(ICreateFolderUseCase):
    def __init__(
        self, folder_factory: IFolderFactory, folder_repository: IFolderRepository
    ) -> None:
        self.folder_factory = folder_factory
        self.folder_repository = folder_repository

    async def execute(self, command: CreateFolderCommand) -> UUID:
        # TODO: Check user rights for assistant_id

        folder = self.folder_factory.create(
            command.name,
            command.description,
            UserId(command.user_id),
            ModelId(command.model_id),
            AssistantId(command.assistant_id),
        )

        await self.folder_repository.add(folder)

        return folder.id.value
