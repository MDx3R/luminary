from uuid import UUID

from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
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
from luminary.model.domain.entity.model import ModelId


class CreateFolderChatUseCase(ICreateFolderChatUseCase):
    def __init__(
        self,
        uow: IUnitOfWork,
        folder_repository: IFolderRepository,
        chat_factory: IChatFactory,
        chat_repository: IChatRepository,
        access_policy: IFolderAccessPolicy,
    ) -> None:
        self.uow = uow
        self.folder_repository = folder_repository
        self.chat_factory = chat_factory
        self.chat_repository = chat_repository
        self.access_policy = access_policy

    async def execute(self, command: CreateFolderChatCommand) -> UUID:
        folder = await self.folder_repository.get_by_id(FolderId(command.folder_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), folder)

        assistant_id = AssistantId.optional(command.assistant_id)
        chat = self.chat_factory.create(
            ChatFactoryDTO(
                user_id=UserId(command.user_id),
                folder_id=FolderId(command.folder_id),
                name=command.name,
                assistant_id=assistant_id,
                settings=ChatSettings(
                    model_id=ModelId(command.model_id),
                    max_context_messages=command.max_context_messages,
                ),
            )
        )

        folder.add_chat(chat.id)

        async with self.uow:
            await self.chat_repository.add(chat)
            await self.folder_repository.save(folder)

        return chat.id.value
