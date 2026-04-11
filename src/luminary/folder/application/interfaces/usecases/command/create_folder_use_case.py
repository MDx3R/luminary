from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateFolderCommand:
    user_id: UUID
    name: str
    description: str | None
    assistant_id: UUID | None


class ICreateFolderUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateFolderCommand) -> UUID: ...
