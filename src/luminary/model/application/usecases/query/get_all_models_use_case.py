from collections.abc import Sequence

from luminary.model.application.dto.model_dto import ModelDTO
from luminary.model.application.interfaces.repositories.model_repository import (
    IModelRepository,
)
from luminary.model.application.interfaces.usecases.query.get_all_models_use_case import (
    IGetAllModelsUseCase,
)


class GetAllModelsUseCase(IGetAllModelsUseCase):
    def __init__(self, model_repository: IModelRepository) -> None:
        self.model_repository = model_repository

    async def execute(self) -> Sequence[ModelDTO]:
        models = await self.model_repository.get_all()
        return [ModelDTO.from_entity(model) for model in models]
