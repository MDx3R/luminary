from common.application.exceptions import NotFoundError
from common.domain.value_objects.id import UserId
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import delete, exists, select

from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.domain.entity.assisnant import Assistant, AssistantId
from luminary.assistant.infrasturcture.database.postgres.sqlalchemy.mappers.assistant_mapper import (
    AssistantMapper,
)
from luminary.assistant.infrasturcture.database.postgres.sqlalchemy.models.assistant_base import (
    AssistantBase,
)


class AssistantRepository(IAssistantRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, id: AssistantId) -> Assistant:
        stmt = select(AssistantBase).where(AssistantBase.assistant_id == id.value)
        result = await self.executor.execute_scalar_one(stmt)
        if not result:
            raise NotFoundError(id)
        return AssistantMapper.to_domain(result)

    async def exists_by_name_for_user(self, name: str, user_id: UserId) -> bool:
        stmt = select(
            exists()
            .where(AssistantBase.name == name)
            .where(AssistantBase.user_id == user_id.value)
        )
        return await self.executor.execute_scalar(stmt)

    async def add(self, entity: Assistant) -> None:
        model = AssistantMapper.to_persistence(entity)
        await self.executor.add(model)

    async def save(self, entity: Assistant) -> None:
        model = AssistantMapper.to_persistence(entity)
        await self.executor.save(model)

    async def remove(self, entity: Assistant) -> None:
        # TODO: Consider soft delete
        stmt = delete(AssistantBase).where(
            AssistantBase.assistant_id == entity.id.value
        )
        await self.executor.execute(stmt)
