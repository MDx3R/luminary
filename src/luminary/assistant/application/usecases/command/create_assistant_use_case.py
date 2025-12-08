from uuid import UUID

from common.domain.value_objects.id import UserId

from luminary.assistant.application.exceptions import AssistantDuplicateNameError
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.create_assistant_use_case import (
    CreateAssistantCommand,
    ICreateAssistantUseCase,
)
from luminary.assistant.domain.interfaces.assistant_factory import IAssistantFactory


class CreateAssistantUseCase(ICreateAssistantUseCase):
    def __init__(
        self,
        assistant_factory: IAssistantFactory,
        assistant_repository: IAssistantRepository,
    ) -> None:
        self.assistant_factory = assistant_factory
        self.assistant_repository = assistant_repository

    async def execute(self, command: CreateAssistantCommand) -> UUID:
        user_id = UserId(command.user_id)

        exists = await self.assistant_repository.exists_by_name_for_user(
            command.name, user_id
        )
        if exists:
            raise AssistantDuplicateNameError(command.user_id, command.name)

        assisnant = self.assistant_factory.create(
            user_id, command.name, command.description, command.prompt
        )

        await self.assistant_repository.add(assisnant)
        return assisnant.id.value
