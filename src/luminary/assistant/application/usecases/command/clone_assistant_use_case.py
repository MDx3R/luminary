from uuid import UUID

from common.domain.interfaces.uuid_generator import IUUIDGenerator
from common.domain.value_objects.id import UserId

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.clone_assistant_use_case import (
    CloneAssistantCommand,
    ICloneAssistantUseCase,
)
from luminary.assistant.domain.entity.assistant import Assistant, AssistantId


class CloneAssistantUseCase(ICloneAssistantUseCase):
    def __init__(
        self,
        repository: IAssistantRepository,
        access_policy: IAssistantAccessPolicy,
        uuid_generator: IUUIDGenerator,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy
        self.uuid_generator = uuid_generator

    async def execute(self, command: CloneAssistantCommand) -> UUID:
        source = await self.repository.get_by_id(AssistantId(command.assistant_id))
        self.access_policy.assert_can_clone(UserId(command.user_id), source)

        new_id = AssistantId(self.uuid_generator.create())
        clone = Assistant.clone(
            source=source,
            new_id=new_id,
            new_owner_id=UserId(command.user_id),
        )

        await self.repository.add(clone)
        return clone.id.value
