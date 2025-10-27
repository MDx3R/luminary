from abc import ABC, abstractmethod

from luminary.source.application.dto.source_dto import SourceDTO, UpdateSourceDTO


class IUpdateSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: UpdateSourceDTO) -> SourceDTO: ...
