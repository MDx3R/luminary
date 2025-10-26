from collections.abc import Sequence
from uuid import UUID

from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select

from luminary.model.application.interfaces.repositories.model_repository import (
    IModelRepository,
)
from luminary.model.domain.entity.model import Model
from luminary.model.infrastructure.database.postgres.sqlalchemy.mappers.model_mapper import (
    ModelMapper,
)
from luminary.model.infrastructure.database.postgres.sqlalchemy.models.model_base import (
    ModelBase,
)


class ModelRepository(IModelRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, model_id: UUID) -> Model:
        stmt = select(ModelBase).where(ModelBase.model_id == model_id)

        result = await self.executor.execute_scalar_one(stmt)
        if not result:
            raise NotFoundError(model_id)
        return ModelMapper.to_domain(result)

    async def get_by_name(self, name: str) -> Model:
        stmt = select(ModelBase).where(ModelBase.name == name)

        result = await self.executor.execute_scalar_one(stmt)
        if not result:
            raise NotFoundError(name)
        return ModelMapper.to_domain(result)

    async def get_all(self) -> Sequence[Model]:
        stmt = select(ModelBase)

        result = await self.executor.execute_scalar_many(stmt)
        return [ModelMapper.to_domain(i) for i in result]

    async def add(self, entity: Model) -> None:
        model = ModelMapper.to_persistence(entity)
        await self.executor.add(model)

    async def save(self, entity: Model) -> None:
        model = ModelMapper.to_persistence(entity)
        await self.executor.save(model)
