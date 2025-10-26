from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.update_assistant_use_case import (
    IUpdateAssistantUseCase,
    UpdateAssistantCommand,
)
from luminary.assistant.domain.entity.assisnant import Instructions


class UpdateAssistantUseCase(IUpdateAssistantUseCase):
    def __init__(
        self,
        assistant_access_policy: IAssistantAccessPolicy,
        assistant_repository: IAssistantRepository,
    ) -> None:
        self.assistant_access_policy = assistant_access_policy
        self.assistant_repository = assistant_repository

    async def execute(self, command: UpdateAssistantCommand) -> None:
        assistant = await self.assistant_repository.get_by_id(command.assistant_id)
        self.assistant_access_policy.assert_is_allowed(command.user_id, assistant)

        assistant.change_name(command.name)
        assistant.change_description(command.description)
        default_prompt = "You're a helpful assistant"  # TODO: Retrieve or define default prompt somewhere
        assistant.change_instructions(Instructions(command.prompt or default_prompt))

        # TODO: Check if assistant has changed

        await self.assistant_repository.save(assistant)
