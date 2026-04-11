from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.domain.entity.assistant import Assistant


class AssistantAccessPolicy(IAssistantAccessPolicy):
    def is_allowed(self, user_id: UserId, entity: Assistant) -> bool:
        return entity.is_owned_by(user_id)

    def assert_is_allowed(self, user_id: UserId, entity: Assistant) -> None:
        if not self.is_allowed(user_id, entity):
            raise AccessPolicyError(
                entity.id, "assistant is accessible only to user who created it"
            )
