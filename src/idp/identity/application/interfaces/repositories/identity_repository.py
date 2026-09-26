from abc import ABC, abstractmethod

from idp.identity.domain.entity.identity import Identity
from idp.identity.domain.value_objects.identity_id import IdentityId


class IIdentityRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: IdentityId) -> Identity: ...
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool: ...
    @abstractmethod
    async def get_by_username(self, username: str) -> Identity: ...
    @abstractmethod
    async def add(self, entity: Identity) -> None: ...
