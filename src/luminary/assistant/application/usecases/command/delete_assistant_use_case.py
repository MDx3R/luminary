from common.domain.value_objects.id import UserId

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.delete_assistant_use_case import (
    DeleteAssistantCommand,
    IDeleteAssistantUseCase,
)
from luminary.assistant.domain.entity.assistant import AssistantId


class DeleteAssistantUseCase(IDeleteAssistantUseCase):
    def __init__(
        self,
        repository: IAssistantRepository,
        access_policy: IAssistantAccessPolicy,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: DeleteAssistantCommand) -> None:
        assistant = await self.repository.get_by_id(AssistantId(command.assistant_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), assistant)

        assistant.delete()

        await self.repository.save(assistant)
