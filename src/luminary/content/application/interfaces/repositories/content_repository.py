from abc import ABC, abstractmethod

from luminary.content.domain.entity.content import Content, ContentId


class IContentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: ContentId) -> Content: ...
    @abstractmethod
    async def add(self, entity: Content) -> None: ...
