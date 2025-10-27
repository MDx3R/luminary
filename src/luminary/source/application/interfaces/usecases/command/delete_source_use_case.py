from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeleteSourceCommand:
    user_id: UUID
    source_id: UUID


class IDeleteSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: DeleteSourceCommand) -> None: ...
