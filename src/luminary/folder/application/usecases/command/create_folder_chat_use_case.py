from uuid import UUID

from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.domain.interfaces.assistant_service import IAssistantService
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.entity.chat import ChatSettings
from luminary.chat.domain.interfaces.chat_factory import IChatFactory
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.create_folder_chat_use_case import (
    CreateFolderChatCommand,
    ICreateFolderChatUseCase,
)


class CreateFolderChatUseCase(ICreateFolderChatUseCase):
    def __init__(
        self,
        chat_factory: IChatFactory,
        assistant_service: IAssistantService,
        assistant_repository: IAssistantRepository,
        folder_repository: IFolderRepository,
        chat_repository: IChatRepository,
    ) -> None:
        self.chat_factory = chat_factory
        self.assistant_service = assistant_service
        self.assistant_repository = assistant_repository
        self.folder_repository = folder_repository
        self.chat_repository = chat_repository

    async def execute(self, command: CreateFolderChatCommand) -> UUID:
        folder = await self.folder_repository.get_by_id(command.folder_id)
        # TODO: Policy

        assistant = await self.assistant_repository.get_by_id(folder.assistant_id)

        chat = self.chat_factory.create(
            folder.folder_id,
            command.user_id,
            name=None,
            settings=ChatSettings(
                folder.model_id,
                assistant.instructions.prompt if assistant.instructions else "prompt",
                20,
            ),
        )

        await self.chat_repository.add(chat)

        return chat.chat_id
