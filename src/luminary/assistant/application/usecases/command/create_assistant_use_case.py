from uuid import UUID

from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.assistant.application.exceptions import AssistantDuplicateNameError
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.create_assistant_use_case import (
    CreateAssistantCommand,
    ICreateAssistantUseCase,
)
from luminary.assistant.domain.entity.assisnant import Assistant, Instructions


class CreateAssistantUseCase(ICreateAssistantUseCase):
    def __init__(
        self, uuid_generator: IUUIDGenerator, assistant_repository: IAssistantRepository
    ) -> None:
        self.uuid_generator = uuid_generator
        self.assistant_repository = assistant_repository

    async def execute(self, command: CreateAssistantCommand) -> UUID:
        exists = await self.assistant_repository.exists_by_name_for_user(
            command.name, command.user_id
        )
        if exists:
            raise AssistantDuplicateNameError(command.user_id, command.name)

        instructions = None
        if command.prompt:
            instructions = Instructions(command.prompt)

        assisnant = Assistant.create(
            self.uuid_generator.create(),
            command.user_id,
            command.name,
            command.description,
            instructions,
        )

        await self.assistant_repository.add(assisnant)
        return assisnant.assistant_id
