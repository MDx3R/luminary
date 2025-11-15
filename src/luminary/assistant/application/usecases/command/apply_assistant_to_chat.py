from common.domain.value_objects.id import UserId

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.application.interfaces.usecases.command.apply_assistant_to_chat import (
    ApplyAssistantToChatCommand,
    IApplyAssistantToChatUseCase,
)
from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.assistant.domain.interfaces.assistant_service import IAssistantService
from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.value_objects.chat_id import ChatId


class ApplyAssistantToChatUseCase(IApplyAssistantToChatUseCase):
    def __init__(
        self,
        assistant_service: IAssistantService,
        assistant_access_policy: IAssistantAccessPolicy,
        assistant_repository: IAssistantRepository,
        chat_repository: IChatRepository,
        chat_access_policy: IChatAccessPolicy,
    ) -> None:
        self.assistant_service = assistant_service
        self.assistant_access_policy = assistant_access_policy
        self.assistant_repository = assistant_repository
        self.chat_repository = chat_repository
        self.chat_access_policy = chat_access_policy

    async def execute(self, command: ApplyAssistantToChatCommand) -> None:
        user_id = UserId(command.user_id)

        assistant = await self.assistant_repository.get_by_id(
            AssistantId(command.assistant_id)
        )
        self.assistant_access_policy.assert_is_allowed(user_id, assistant)

        chat = await self.chat_repository.get_by_id(ChatId(command.chat_id))
        self.chat_access_policy.assert_is_allowed(user_id, chat)

        self.assistant_service.apply_assistant_instructions_to_chat(assistant, chat)

        await self.chat_repository.save(chat)
