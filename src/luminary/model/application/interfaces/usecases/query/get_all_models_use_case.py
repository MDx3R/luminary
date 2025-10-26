from abc import ABC, abstractmethod
from collections.abc import Sequence

from luminary.model.application.dto.model_dto import ModelDTO


class IGetAllModelsUseCase(ABC):
    @abstractmethod
    async def execute(self) -> Sequence[ModelDTO]: ...
