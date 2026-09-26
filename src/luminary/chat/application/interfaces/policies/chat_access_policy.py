from common.application.interfaces.policies.access_policy import IAccessPolicy

from luminary.chat.domain.entity.chat import Chat


class IChatAccessPolicy(IAccessPolicy[Chat]): ...
