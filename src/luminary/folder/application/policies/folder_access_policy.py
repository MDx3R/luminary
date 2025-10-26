from uuid import UUID

from common.application.exceptions import AccessPolicyError

from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.domain.entity.folder import Folder


class FolderAccessPolicy(IFolderAccessPolicy):
    def is_allowed(self, user_id: UUID, folder: Folder) -> bool:
        return folder.user_id == user_id

    def assert_is_allowed(self, user_id: UUID, folder: Folder) -> None:
        if not self.is_allowed(user_id, folder):
            raise AccessPolicyError(
                folder.folder_id,
                "folder is accessable only to user who created it",
            )
