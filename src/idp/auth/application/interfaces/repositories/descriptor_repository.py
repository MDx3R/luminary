from abc import ABC, abstractmethod
from uuid import UUID

from idp.identity.domain.value_objects.descriptor import IdentityDescriptor


class IIdentityDescriptorRepository(ABC):
    @abstractmethod
    async def get_by_id(self, identity_id: UUID) -> IdentityDescriptor: ...
