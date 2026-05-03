from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.domain.entity.assistant import Assistant
from luminary.assistant.domain.enums import AssistantType


class AssistantAccessPolicy(IAssistantAccessPolicy):
    def is_allowed(self, user_id: UserId, entity: Assistant) -> bool:
        if entity.type == AssistantType.SYSTEM:
            return False
        return entity.is_owned_by(user_id)

    def assert_is_allowed(self, user_id: UserId, entity: Assistant) -> None:
        if entity.type == AssistantType.SYSTEM:
            raise AccessPolicyError(entity.id, "system assistants cannot be modified")
        if not entity.is_owned_by(user_id):
            raise AccessPolicyError(
                entity.id, "assistant is accessible only to user who created it"
            )
