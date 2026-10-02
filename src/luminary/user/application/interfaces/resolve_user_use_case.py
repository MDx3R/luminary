from abc import ABC, abstractmethod

from common.application.value_objects.descriptor import IdentityDescriptor


class IResolveUserUseCase(ABC):
    @abstractmethod
    async def execute(
        self, subject: str, username: str, access_token: str
    ) -> IdentityDescriptor: ...
