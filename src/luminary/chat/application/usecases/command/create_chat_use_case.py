from decimal import Decimal
from uuid import UUID, uuid4

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import (
    CreateChatCommand,
    ICreateChatUseCase,
)
from luminary.chat.domain.entity.chat import ChatSettings
from luminary.chat.domain.interfaces.chat_factory import IChatFactory
from luminary.model.domain.entity.model import Model


class CreateChatUseCase(ICreateChatUseCase):
    DEFAULT_MODEL_NAME: str = "gemini-2.5-flash-lite"
    DEFAULT_PROMPT: str = "You are a helpful assistant"

    def __init__(
        self, chat_factory: IChatFactory, chat_repository: IChatRepository
    ) -> None:
        self.chat_factory = chat_factory
        self.chat_repository = chat_repository

    async def execute(self, command: CreateChatCommand) -> UUID:
        # TODO: Add repo call
        model = Model(
            uuid4(), self.DEFAULT_MODEL_NAME, "desc", Decimal(10), Decimal(10)
        )

        # TODO: Fetch default settings from repo

        chat = self.chat_factory.create(
            user_id=command.user_id,
            folder_id=None,
            name=None,
            settings=ChatSettings(
                model_id=model.model_id,
                system_prompt=self.DEFAULT_PROMPT,
                max_context_messages=20,
            ),
        )

        await self.chat_repository.add(chat)

        return chat.chat_id
