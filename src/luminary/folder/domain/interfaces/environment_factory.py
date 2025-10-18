from abc import ABC, abstractmethod
from uuid import UUID

from luminary.folder.domain.entity.environment import Environment


class IEnvironmentFactory(ABC):
    @abstractmethod
    def create(
        self,
        name: str,
        description: str | None,
        user_id: UUID,
        model_id: UUID,
        assistant_id: UUID,
    ) -> Environment: ...
