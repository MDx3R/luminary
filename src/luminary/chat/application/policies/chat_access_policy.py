from uuid import UUID

from common.application.exceptions import AccessPolicyError

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.domain.entity.chat import Chat


class ChatAccessPolicy(IChatAccessPolicy):
    def is_allowed(self, user_id: UUID, chat: Chat) -> bool:
        return chat.user_id == user_id

    def assert_is_allowed(self, user_id: UUID, chat: Chat) -> None:
        if not self.is_allowed(user_id, chat):
            raise AccessPolicyError(
                chat.chat_id, "chat is accessable only to user who created it"
            )
