from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Self
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class Event(ABC):
    event_id: UUID | None = None
    event_version: int = 1

    def set_event_version(self, version: int) -> Self:
        new = replace(self, event_version=version)
        return new

    def set_event_id(self, event_id: UUID) -> Self:
        new = replace(self, event_id=event_id)
        return new

    @property
    @abstractmethod
    def aggregate_id(self) -> UUID: ...

    @classmethod
    @abstractmethod
    def aggregate_type(cls) -> str: ...

    @classmethod
    def event_type(cls) -> str:
        return cls.__name__
