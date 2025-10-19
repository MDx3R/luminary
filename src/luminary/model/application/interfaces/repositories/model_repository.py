from abc import ABC, abstractmethod
from uuid import UUID

from luminary.model.domain.entity.model import Model


class IModelRepository(ABC):
    @abstractmethod
    async def get_by_id(self, model_id: UUID) -> Model: ...
    @abstractmethod
    async def get_by_name(self, name: str) -> Model: ...
    @abstractmethod
    async def add(self, entity: Model) -> None: ...
    @abstractmethod
    async def save(self, entity: Model) -> None: ...
