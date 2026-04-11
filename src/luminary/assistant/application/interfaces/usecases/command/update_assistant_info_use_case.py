from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateAssistantInfoCommand:
    user_id: UUID
    assistant_id: UUID
    name: str
    description: str


class IUpdateAssistantInfoUseCase(ABC):
    @abstractmethod
    async def execute(self, command: UpdateAssistantInfoCommand) -> None: ...
