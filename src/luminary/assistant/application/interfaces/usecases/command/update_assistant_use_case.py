from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateAssistantCommand:
    user_id: UUID
    assistant_id: UUID
    name: str
    description: str
    prompt: str | None


class IUpdateAssistantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: UpdateAssistantCommand) -> None: ...
