from abc import ABC, abstractmethod

from luminary.user.application.dtos.profile import ExternalProfile


class IProfileProvider(ABC):
    @abstractmethod
    async def get_profile(self, access_token: str) -> ExternalProfile: ...
