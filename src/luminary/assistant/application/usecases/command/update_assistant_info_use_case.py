from common.domain.value_objects.id import UserId

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.update_assistant_info_use_case import (
    IUpdateAssistantInfoUseCase,
    UpdateAssistantInfoCommand,
)
from luminary.assistant.domain.entity.assistant import AssistantId


class UpdateAssistantInfoUseCase(IUpdateAssistantInfoUseCase):
    def __init__(
        self,
        repository: IAssistantRepository,
        access_policy: IAssistantAccessPolicy,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: UpdateAssistantInfoCommand) -> None:
        assistant = await self.repository.get_by_id(AssistantId(command.assistant_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), assistant)

        if assistant.info_matches(command.name, command.description):
            return

        assistant.change_name(command.name)
        assistant.change_description(command.description)
        await self.repository.save(assistant)
