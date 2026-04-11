from common.domain.value_objects.id import UserId

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.update_assistant_instructions_use_case import (
    IUpdateAssistantInstructionsUseCase,
    UpdateAssistantInstructionsCommand,
)
from luminary.assistant.domain.entity.assistant import AssistantId, Instructions


class UpdateAssistantInstructionsUseCase(IUpdateAssistantInstructionsUseCase):
    def __init__(
        self,
        repository: IAssistantRepository,
        access_policy: IAssistantAccessPolicy,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: UpdateAssistantInstructionsCommand) -> None:
        assistant = await self.repository.get_by_id(AssistantId(command.assistant_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), assistant)

        if assistant.instructions_matches(command.prompt):
            return

        assistant.change_instructions(Instructions(prompt=command.prompt))
        await self.repository.save(assistant)
