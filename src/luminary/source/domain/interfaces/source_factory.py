from abc import ABC, abstractmethod
from uuid import UUID

from luminary.source.domain.entity.source import Source


class ISourceFactory(ABC):
    @abstractmethod
    def create(self, user_id: UUID, name: str) -> Source: ...
