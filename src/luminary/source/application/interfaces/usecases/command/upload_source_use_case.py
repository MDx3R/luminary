from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UploadSourceCommand:
    user_id: UUID
    source_id: UUID
    file_path: str


class IUploadSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: UploadSourceCommand) -> None: ...
