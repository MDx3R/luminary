from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.change_chat_assistant_use_case import (
    ChangeChatAssistantCommand,
    IChangeChatAssistantUseCase,
)
from luminary.chat.domain.value_objects.chat_id import ChatId


class ChangeChatAssistantUseCase(IChangeChatAssistantUseCase):
    def __init__(
        self,
        repository: IChatRepository,
        access_policy: IChatAccessPolicy,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: ChangeChatAssistantCommand) -> None:
        chat = await self.repository.get_by_id(ChatId(command.chat_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), chat)

        if chat.assistant_matches(AssistantId(command.assistant_id)):
            return

        chat.apply_assistant(AssistantId(command.assistant_id))
        await self.repository.save(chat)
