from uuid import UUID

from common.application.exceptions import NotFoundError
from common.presentation.http.fastapi.auth import require_authenticated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_utils.cbv import cbv

from luminary.model.application.interfaces.usecases.query.get_all_models_use_case import (
    IGetAllModelsUseCase,
)
from luminary.model.application.interfaces.usecases.query.get_model_by_id_use_case import (
    GetModelByIdQuery,
    IGetModelByIdUseCase,
)
from luminary.model.presentation.http.dto.response import ModelResponse


model_query_router = APIRouter()


@cbv(model_query_router)
class ModelQueryController:
    get_model_by_id_use_case: IGetModelByIdUseCase = Depends()
    get_all_models_use_case: IGetAllModelsUseCase = Depends()

    @model_query_router.get(
        "/{model_id}", dependencies=[Depends(require_authenticated)]
    )
    async def get_by_id(
        self,
        model_id: UUID,
    ) -> ModelResponse:
        try:
            model_dto = await self.get_model_by_id_use_case.execute(
                GetModelByIdQuery(model_id=model_id)
            )
            return ModelResponse.from_dto(model_dto)
        except NotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "ModelNotFoundError",
                    "model_id": str(exc.entity_id),
                    "message": str(exc),
                },
            ) from exc

    @model_query_router.get("/", dependencies=[Depends(require_authenticated)])
    async def get_all(self) -> list[ModelResponse]:
        models_dto = await self.get_all_models_use_case.execute()
        return [ModelResponse.from_dto(model_dto) for model_dto in models_dto]
