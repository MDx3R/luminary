from uuid import UUID

from common.domain.value_objects.id import UserId

from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.create_assistant_use_case import (
    CreateAssistantCommand,
    ICreateAssistantUseCase,
)
from luminary.assistant.domain.enums import AssistantType
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
        assistant = self.assistant_factory.create(
            user_id=UserId(command.user_id),
            name=command.name,
            description=command.description,
            prompt=command.prompt,
            type=AssistantType.PERSONAL,
        )

        await self.assistant_repository.add(assistant)

        return assistant.id.value
