from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CloneAssistantCommand:
    user_id: UUID
    assistant_id: UUID


class ICloneAssistantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CloneAssistantCommand) -> UUID: ...
