from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateAssistantInstructionsCommand:
    user_id: UUID
    assistant_id: UUID
    prompt: str


class IUpdateAssistantInstructionsUseCase(ABC):
    @abstractmethod
    async def execute(self, command: UpdateAssistantInstructionsCommand) -> None: ...
