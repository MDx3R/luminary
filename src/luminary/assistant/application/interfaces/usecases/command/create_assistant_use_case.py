from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateAssistantCommand:
    user_id: UUID
    name: str
    description: str
    prompt: str | None


class ICreateAssistantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateAssistantCommand) -> UUID: ...
