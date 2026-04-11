from common.application.interfaces.policies.access_policy import IAccessPolicy

from luminary.assistant.domain.entity.assistant import Assistant


class IAssistantAccessPolicy(IAccessPolicy[Assistant]): ...
