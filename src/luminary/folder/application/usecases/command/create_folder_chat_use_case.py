from uuid import UUID

from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from common.domain.value_objects.id import UserId

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.interfaces.chat_factory import ChatFactoryDTO, IChatFactory
from luminary.chat.domain.value_objects.chat_settings import ChatSettings
from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.create_folder_chat_use_case import (
    CreateFolderChatCommand,
    ICreateFolderChatUseCase,
)
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.model.application.interfaces.repositories.model_repository import (
    IModelRepository,
)


class CreateFolderChatUseCase(ICreateFolderChatUseCase):
    DEFAULT_MODEL_NAME: str = "gemini-2.5-flash-lite"

    def __init__(  # noqa: PLR0913
        self,
        uow: IUnitOfWork,
        chat_factory: IChatFactory,
        folder_access_policy: IFolderAccessPolicy,
        folder_repository: IFolderRepository,
        chat_repository: IChatRepository,
        model_repository: IModelRepository,
    ) -> None:
        self.uow = uow
        self.chat_factory = chat_factory
        self.folder_access_policy = folder_access_policy
        self.folder_repository = folder_repository
        self.chat_repository = chat_repository
        self.model_repository = model_repository

    async def execute(self, command: CreateFolderChatCommand) -> UUID:
        user_id = UserId(command.user_id)
        folder_id = FolderId(command.folder_id)

        folder = await self.folder_repository.get_by_id(folder_id)
        self.folder_access_policy.assert_is_allowed(user_id, folder)

        model = await self.model_repository.get_by_name(self.DEFAULT_MODEL_NAME)

        # TODO: Define chat service
        chat = self.chat_factory.create(
            ChatFactoryDTO(
                user_id,
                folder_id,
                name=None,
                assisnant_id=folder.assistant_id,
                settings=ChatSettings(model.id, 20),
            )
        )

        for source_id in folder.sources:
            chat.add_source(source_id)

        folder.add_chat(chat.id)

        async with self.uow:
            await self.chat_repository.add(chat)
            await self.folder_repository.save(folder)

        return chat.id.value
