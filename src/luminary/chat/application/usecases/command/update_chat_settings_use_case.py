from common.domain.value_objects.id import UserId

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.update_chat_settings_use_case import (
    IUpdateChatSettingsUseCase,
    UpdateChatSettingsCommand,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.model.domain.entity.model import ModelId


class UpdateChatSettingsUseCase(IUpdateChatSettingsUseCase):
    def __init__(
        self,
        repository: IChatRepository,
        access_policy: IChatAccessPolicy,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: UpdateChatSettingsCommand) -> None:
        chat = await self.repository.get_by_id(ChatId(command.chat_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), chat)

        model_id = ModelId(command.model_id)
        if chat.model_config_matches(model_id, command.max_context_messages):
            return

        chat.update_model_and_context(model_id, command.max_context_messages)
        await self.repository.save(chat)
