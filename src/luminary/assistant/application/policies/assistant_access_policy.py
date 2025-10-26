from uuid import UUID

from common.application.exceptions import AccessPolicyError

from luminary.assistant.application.interfaces.policies.assistant_access_policy import (
    IAssistantAccessPolicy,
)
from luminary.assistant.domain.entity.assisnant import Assistant


class AssistantAccessPolicy(IAssistantAccessPolicy):
    def is_allowed(self, user_id: UUID, assistant: Assistant) -> bool:
        return assistant.user_id == user_id

    def assert_is_allowed(self, user_id: UUID, assistant: Assistant) -> None:
        if not self.is_allowed(user_id, assistant):
            raise AccessPolicyError(
                assistant.assistant_id,
                "assistant is accessable only to user who created it",
            )
