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
from luminary.assistant.domain.entity.assisnant import AssistantId


class DeleteAssistantUseCase(IDeleteAssistantUseCase):
    def __init__(
        self,
        assistant_access_policy: IAssistantAccessPolicy,
        assistant_repository: IAssistantRepository,
    ) -> None:
        self.assistant_access_policy = assistant_access_policy
        self.assistant_repository = assistant_repository

    async def execute(self, command: DeleteAssistantCommand) -> None:
        assistant = await self.assistant_repository.get_by_id(
            AssistantId(command.assistant_id)
        )
        self.assistant_access_policy.assert_is_allowed(
            UserId(command.user_id), assistant
        )

        assistant.delete()

        # TODO: Eventual consistency
        await self.assistant_repository.save(assistant)
