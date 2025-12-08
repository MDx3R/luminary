from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId

from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.domain.entity.source import Source


class SourceAccessPolicy(ISourceAccessPolicy):
    def is_allowed(self, user_id: UserId, entity: Source) -> bool:
        return entity.is_owned_by(user_id)

    def assert_is_allowed(self, user_id: UserId, entity: Source) -> None:
        if not self.is_allowed(user_id, entity):
            raise AccessPolicyError(
                entity.id, "source is accessable only to user who created it"
            )
