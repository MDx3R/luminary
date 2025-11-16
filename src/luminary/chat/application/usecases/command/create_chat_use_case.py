from uuid import UUID

from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import (
    CreateChatCommand,
    ICreateChatUseCase,
)
from luminary.chat.domain.interfaces.chat_factory import ChatFactoryDTO, IChatFactory
from luminary.chat.domain.value_objects.chat_settings import ChatSettings
from luminary.model.application.interfaces.repositories.model_repository import (
    IModelRepository,
)


class CreateChatUseCase(ICreateChatUseCase):
    DEFAULT_MODEL_NAME: str = "gemini-2.5-flash-lite"
    DEFAULT_PROMPT: str = "You are a helpful assistant"
    MAX_CONTEXT_MESSAGES: int = 20

    def __init__(
        self,
        chat_factory: IChatFactory,
        chat_repository: IChatRepository,
        model_repository: IModelRepository,
    ) -> None:
        self.chat_factory = chat_factory
        self.chat_repository = chat_repository
        self.model_repository = model_repository

    async def execute(self, command: CreateChatCommand) -> UUID:
        model = await self.model_repository.get_by_name(self.DEFAULT_MODEL_NAME)

        # TODO: Fetch default settings from repo

        assisnant_id = None
        if command.assistant_id:
            assisnant_id = AssistantId(command.assistant_id)

        # TODO: Assistant access policy

        chat = self.chat_factory.create(
            ChatFactoryDTO(
                user_id=UserId(command.user_id),
                folder_id=None,
                name=None,
                assisnant_id=assisnant_id,  # TODO
                settings=ChatSettings(
                    model_id=model.id,
                    max_context_messages=self.MAX_CONTEXT_MESSAGES,
                ),
            )
        )

        await self.chat_repository.add(chat)

        return chat.id.value
