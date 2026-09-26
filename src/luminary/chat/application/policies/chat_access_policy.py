from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.domain.entity.chat import Chat


class ChatAccessPolicy(IChatAccessPolicy):
    def is_allowed(self, user_id: UserId, entity: Chat) -> bool:
        return entity.is_owned_by(user_id)

    def assert_is_allowed(self, user_id: UserId, entity: Chat) -> None:
        if not self.is_allowed(user_id, entity):
            raise AccessPolicyError(
                entity.id, "chat is accessible only to user who created it"
            )
