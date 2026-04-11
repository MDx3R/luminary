from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId

from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.domain.entity.folder import Folder


class FolderAccessPolicy(IFolderAccessPolicy):
    def is_allowed(self, user_id: UserId, entity: Folder) -> bool:
        return entity.is_owned_by(user_id)

    def assert_is_allowed(self, user_id: UserId, entity: Folder) -> None:
        if not self.is_allowed(user_id, entity):
            raise AccessPolicyError(
                entity.id, "folder is accessible only to user who created it"
            )
