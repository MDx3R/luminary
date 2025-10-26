from abc import ABC, abstractmethod
from uuid import UUID

from luminary.source.domain.entity.source import Source


class ISourceAccessPolicy(ABC):
    @abstractmethod
    def is_allowed(self, user_id: UUID, source: Source) -> bool: ...

    @abstractmethod
    def assert_is_allowed(self, user_id: UUID, source: Source) -> None: ...
