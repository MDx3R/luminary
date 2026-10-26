from abc import ABC, abstractmethod
from uuid import UUID

from luminary.user.application.dtos.profile import ExternalProfile, UserProfile


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_subject(self, subject: str) -> UserProfile | None: ...

    @abstractmethod
    async def upsert(self, user_id: UUID, profile: ExternalProfile) -> UserProfile: ...
