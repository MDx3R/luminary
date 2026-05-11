from abc import abstractmethod

from common.application.interfaces.policies.access_policy import IAccessPolicy
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import Assistant


class IAssistantAccessPolicy(IAccessPolicy[Assistant]):
    @abstractmethod
    def assert_can_clone(self, user_id: UserId, entity: Assistant) -> None: ...
