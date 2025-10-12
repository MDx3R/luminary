from abc import ABC, abstractmethod
from uuid import UUID


class CreateAssistantCommand:
    user_id: UUID
    name: str
    description: str
    prompt: str


class ICreateAssistantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateAssistantCommand) -> UUID: ...
