from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AddFileToEnvironmentCommand:
    user_id: UUID
    environment_id: UUID
    file_id: UUID


class IAddFileToEnvironmentUseCase(ABC):
    @abstractmethod
    async def execute(self, command: AddFileToEnvironmentCommand) -> None: ...
