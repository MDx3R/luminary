from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeleteAssistantCommand:
    user_id: UUID
    assistant_id: UUID


class IDeleteAssistantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: DeleteAssistantCommand) -> None: ...
