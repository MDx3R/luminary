from abc import ABC, abstractmethod
from uuid import UUID

from luminary.source.domain.entity.source import Source


class ISourceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, source_id: UUID) -> Source: ...
    @abstractmethod
    async def add(self, entity: Source) -> None: ...
    @abstractmethod
    async def save(self, entity: Source) -> None: ...
    @abstractmethod
    async def remove(self, entity: Source) -> None: ...
