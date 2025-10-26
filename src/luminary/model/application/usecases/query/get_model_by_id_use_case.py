from common.application.exceptions import NotFoundError

from luminary.model.application.dto.model_dto import ModelDTO
from luminary.model.application.interfaces.repositories.model_repository import (
    IModelRepository,
)
from luminary.model.application.interfaces.usecases.query.get_model_by_id_use_case import (
    GetModelByIdQuery,
    IGetModelByIdUseCase,
)


class GetModelByIdUseCase(IGetModelByIdUseCase):
    def __init__(self, model_repository: IModelRepository) -> None:
        self.model_repository = model_repository

    async def execute(self, query: GetModelByIdQuery) -> ModelDTO:
        try:
            model = await self.model_repository.get_by_id(query.model_id)
            return ModelDTO.from_entity(model)
        except NotFoundError as exc:
            raise NotFoundError(exc.entity_id) from exc
