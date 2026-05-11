from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class PublishAssistantCommand:
    user_id: UUID
    assistant_id: UUID


class IPublishAssistantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: PublishAssistantCommand) -> None: ...
