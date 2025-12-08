from abc import ABC, abstractmethod

from luminary.source.domain.entity.source import Source, SourceId


class ISourceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: SourceId) -> Source: ...
    @abstractmethod
    async def add(self, entity: Source) -> None: ...
    @abstractmethod
    async def save(self, entity: Source) -> None: ...
    @abstractmethod
    async def remove(self, entity: Source) -> None: ...
