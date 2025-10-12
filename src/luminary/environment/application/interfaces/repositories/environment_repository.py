from abc import ABC, abstractmethod
from uuid import UUID

from luminary.environment.domain.entity.environment import Environment


class IEnvironmentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, environment_id: UUID) -> Environment: ...
    @abstractmethod
    async def add(self, entity: Environment) -> None: ...
    @abstractmethod
    async def save(self, entity: Environment) -> None: ...
