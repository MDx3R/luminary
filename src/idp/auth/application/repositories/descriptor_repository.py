from uuid import UUID

from idp.auth.application.interfaces.repositories.descriptor_repository import (
    IIdentityDescriptorRepository,
)
from idp.identity.application.interfaces.repositories.identity_repository import (
    IIdentityRepository,
)
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor
from idp.identity.domain.value_objects.identity_id import IdentityId


class IdentityDescriptorRepository(IIdentityDescriptorRepository):
    def __init__(self, identity_repository: IIdentityRepository) -> None:
        self.identity_repository = identity_repository

    async def get_by_id(self, identity_id: UUID) -> IdentityDescriptor:
        identity = await self.identity_repository.get_by_id(IdentityId(identity_id))
        return IdentityDescriptor(
            identity_id=identity.id.value, username=identity.username.value
        )
