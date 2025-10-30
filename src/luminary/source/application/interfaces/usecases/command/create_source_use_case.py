from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateSourceCommand:
    user_id: UUID
    name: str


class ICreateSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateSourceCommand) -> UUID: ...
