from abc import ABC, abstractmethod

from common.domain.value_objects.id import UserId

from luminary.content.domain.entity.content import Content


class IContentFactory(ABC):
    @abstractmethod
    def create(self, user_id: UserId, bucket: str, mime: str, size: int) -> Content: ...
