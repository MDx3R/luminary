from abc import ABC, abstractmethod

from luminary.content.domain.entity.content import Content


class IContentRepository(ABC):
    @abstractmethod
    async def add(self, entity: Content) -> None: ...
