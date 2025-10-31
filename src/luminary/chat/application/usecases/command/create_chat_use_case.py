from uuid import UUID

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import (
    CreateChatCommand,
    ICreateChatUseCase,
)
from luminary.chat.domain.entity.chat import ChatSettings
from luminary.chat.domain.interfaces.chat_factory import IChatFactory
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

        chat = self.chat_factory.create(
            user_id=command.user_id,
            folder_id=None,
            name=None,
            settings=ChatSettings(
                model_id=model.model_id,
                system_prompt=self.DEFAULT_PROMPT,
                max_context_messages=self.MAX_CONTEXT_MESSAGES,
            ),
        )

        await self.chat_repository.add(chat)

        return chat.chat_id
