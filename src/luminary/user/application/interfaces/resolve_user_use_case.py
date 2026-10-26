from abc import ABC, abstractmethod

from common.application.value_objects.descriptor import IdentityDescriptor

from luminary.user.application.dtos.profile import ExternalProfile


class IResolveUserUseCase(ABC):
    @abstractmethod
    async def execute(
        self, profile: ExternalProfile, username: str
    ) -> IdentityDescriptor: ...
