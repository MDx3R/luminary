from uuid import UUID, uuid4

from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.entity.chat import ChatSettings
from luminary.chat.domain.interfaces.chat_factory import ChatFactoryDTO, IChatFactory
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
        self,
        uow: IUnitOfWork,
        folder_factory: IFolderFactory,
        chat_factory: IChatFactory,
        folder_repository: IFolderRepository,
        chat_repository: IChatRepository,
    ) -> None:
        self.uow = uow
        self.folder_factory = folder_factory
        self.chat_factory = chat_factory
        self.folder_repository = folder_repository
        self.chat_repository = chat_repository

    async def execute(self, command: CreateFolderCommand) -> UUID:
        folder = self.folder_factory.create(
            command.name,
            command.description,
            command.user_id,
            command.model_id,
            command.assistant_id,
        )
        chat = self.chat_factory.create(
            ChatFactoryDTO(
                folder.folder_id,
                command.user_id,
                name=None,
                settings=ChatSettings(
                    uuid4(), "prompt", 10
                ),  # TODO: Replace with assistant service call
            )
        )

        async with self.uow:
            await self.folder_repository.add(folder)
            await self.chat_repository.add(chat)

        return folder.folder_id
