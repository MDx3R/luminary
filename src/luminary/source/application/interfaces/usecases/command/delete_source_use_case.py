from abc import ABC, abstractmethod

from luminary.source.application.dto.source_dto import DeleteSourceDTO


class IDeleteSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: DeleteSourceDTO) -> None: ...
