from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateEditorContentCommand:
    user_id: UUID
    folder_id: UUID
    text: str


class IUpdateEditorContentUseCase(ABC):
    @abstractmethod
    async def execute(self, command: UpdateEditorContentCommand) -> None: ...
