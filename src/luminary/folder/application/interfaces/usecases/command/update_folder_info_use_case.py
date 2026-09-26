from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateFolderInfoCommand:
    user_id: UUID
    folder_id: UUID
    name: str
    description: str | None


class IUpdateFolderInfoUseCase(ABC):
    @abstractmethod
    async def execute(self, command: UpdateFolderInfoCommand) -> None: ...
