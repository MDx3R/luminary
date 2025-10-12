from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateEnvironmentCommand:
    user_id: UUID
    name: str
    description: str | None
    model_id: UUID
    assistant_id: UUID


class ICreateEnvironmentUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateEnvironmentCommand) -> UUID: ...
