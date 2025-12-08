from common.application.interfaces.policies.access_policy import IAccessPolicy

from luminary.folder.domain.entity.folder import Folder


class IFolderAccessPolicy(IAccessPolicy[Folder]): ...
