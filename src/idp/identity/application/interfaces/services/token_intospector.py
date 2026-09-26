from abc import ABC, abstractmethod
from uuid import UUID

from idp.identity.domain.value_objects.descriptor import IdentityDescriptor


class ITokenIntrospector(ABC):
    @abstractmethod
    async def extract_user(self, token: str) -> IdentityDescriptor: ...
    @abstractmethod
    async def is_token_valid(self, token: str) -> bool: ...
    @abstractmethod
    async def validate(self, token: str) -> UUID: ...
