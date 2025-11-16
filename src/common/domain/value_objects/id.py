from abc import ABC
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class EntityId(ABC):
    value: UUID


@dataclass(frozen=True)
class UserId(EntityId): ...
