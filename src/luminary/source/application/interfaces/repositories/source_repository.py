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
    async def delete(self, source_id: UUID) -> None: ...

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[Source]: ...

    @abstractmethod
    async def exists(self, source_id: UUID) -> bool: ...

    @abstractmethod
    async def count_by_user(self, user_id: UUID) -> int: ...
