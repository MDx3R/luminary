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
from luminary.chat.domain.value_objects.chat_settings import ChatSettings
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

        new_settings = ChatSettings(
            model_id=ModelId(command.model_id),
            max_context_messages=command.max_context_messages,
        )

        if chat.settings_matches(new_settings):
            return

        chat.change_settings(new_settings)
        await self.repository.save(chat)
