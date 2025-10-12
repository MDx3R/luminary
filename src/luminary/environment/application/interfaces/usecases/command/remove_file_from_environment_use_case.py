from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RemoveFileFromEnvironmentCommand:
    user_id: UUID
    environment_id: UUID
    file_id: UUID


class IRemoveFileFromEnvironmentUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RemoveFileFromEnvironmentCommand) -> None: ...
