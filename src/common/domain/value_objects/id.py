from abc import ABC
from dataclasses import dataclass
from typing import Self
from uuid import UUID


@dataclass(frozen=True)
class EntityId(ABC):
    value: UUID

    @classmethod
    def optional(cls, value: UUID | None = None) -> Self | None:
        if value is None:
            return None

        return cls(value=value)


@dataclass(frozen=True)
class UserId(EntityId): ...
