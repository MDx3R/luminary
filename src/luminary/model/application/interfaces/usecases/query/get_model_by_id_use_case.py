from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from luminary.model.application.dto.model_dto import ModelDTO


@dataclass(frozen=True)
class GetModelByIdQuery:
    model_id: UUID


class IGetModelByIdUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetModelByIdQuery) -> ModelDTO: ...
