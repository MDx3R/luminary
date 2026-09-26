from common.application.interfaces.policies.access_policy import IAccessPolicy

from luminary.source.domain.entity.source import Source


class ISourceAccessPolicy(IAccessPolicy[Source]): ...
