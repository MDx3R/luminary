from uuid import UUID

from common.application.exceptions import AccessPolicyError

from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.domain.entity.source import Source


class SourceAccessPolicy(ISourceAccessPolicy):
    def is_allowed(self, user_id: UUID, source: Source) -> bool:
        return source.is_owned_by(user_id)

    def assert_is_allowed(self, user_id: UUID, source: Source) -> None:
        if not self.is_allowed(user_id, source):
            raise AccessPolicyError(
                source.source_id,
                "source is accessable only to user who created it",
            )
