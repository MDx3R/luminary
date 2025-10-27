from abc import ABC, abstractmethod

from luminary.source.application.dto.source_dto import CreateSourceDTO, SourceDTO


class ICreateSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: CreateSourceDTO) -> SourceDTO: ...
