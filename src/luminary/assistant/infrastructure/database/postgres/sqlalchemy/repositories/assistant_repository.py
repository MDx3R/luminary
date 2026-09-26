from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select

from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.domain.entity.assistant import Assistant, AssistantId
from luminary.assistant.infrastructure.database.postgres.sqlalchemy.mappers.assistant_mapper import (
    AssistantMapper,
)
from luminary.assistant.infrastructure.database.postgres.sqlalchemy.models.assistant_base import (
    AssistantBase,
)


class AssistantRepository(IAssistantRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, id: AssistantId) -> Assistant:
        stmt = (
            select(AssistantBase)
            .where(AssistantBase.assistant_id == id.value)
            .where(AssistantBase.is_active)
        )
        result = await self.executor.execute_scalar_one(stmt)
        if result is None:
            raise NotFoundError(id)
        return AssistantMapper.to_domain(result)

    async def add(self, entity: Assistant) -> None:
        model = AssistantMapper.to_persistence(entity)
        await self.executor.add(model)

    async def save(self, entity: Assistant) -> None:
        model = AssistantMapper.to_persistence(entity)
        await self.executor.save(model)
