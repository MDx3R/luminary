from uuid import UUID

from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import (
    CreateChatCommand,
    ICreateChatUseCase,
)
from luminary.chat.domain.interfaces.chat_factory import ChatFactoryDTO, IChatFactory
from luminary.chat.domain.value_objects.chat_settings import ChatSettings
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.model.domain.entity.model import ModelId


class CreateChatUseCase(ICreateChatUseCase):
    def __init__(
        self,
        chat_factory: IChatFactory,
        chat_repository: IChatRepository,
    ) -> None:
        self.chat_factory = chat_factory
        self.chat_repository = chat_repository

    async def execute(self, command: CreateChatCommand) -> UUID:
        folder_id = FolderId.optional(command.folder_id)
        assistant_id = AssistantId.optional(command.assistant_id)
        chat = self.chat_factory.create(
            ChatFactoryDTO(
                user_id=UserId(command.user_id),
                folder_id=folder_id,
                name=command.name,
                assistant_id=assistant_id,
                settings=ChatSettings(
                    model_id=ModelId(command.model_id),
                    max_context_messages=command.max_context_messages,
                ),
            )
        )
        await self.chat_repository.add(chat)
        return chat.id.value
