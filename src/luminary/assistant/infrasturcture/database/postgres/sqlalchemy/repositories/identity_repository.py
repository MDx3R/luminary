from uuid import UUID

from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import exists, select

from luminary.assistant.application.interfaces.repositories.assistant_repository import (
    IAssistantRepository,
)
from luminary.assistant.domain.entity.assisnant import Assistant
from luminary.assistant.infrasturcture.database.postgres.sqlalchemy.mappers.identity_mapper import (
    AssistantMapper,
)
from luminary.assistant.infrasturcture.database.postgres.sqlalchemy.models.identity_base import (
    AssistantBase,
)


class AssistantRepository(IAssistantRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, assistant_id: UUID) -> Assistant:
        stmt = select(AssistantBase).where(AssistantBase.assistant_id == assistant_id)
        result = await self.executor.execute_scalar_one(stmt)
        if not result:
            raise NotFoundError(assistant_id)
        return AssistantMapper.to_domain(result)

    async def exists_by_name_for_user(self, name: str, user_id: UUID) -> bool:
        stmt = select(
            exists()
            .where(AssistantBase.name == name)
            .where(AssistantBase.user_id == user_id)
        )
        return await self.executor.execute_scalar(stmt)

    async def add(self, entity: Assistant) -> None:
        model = AssistantMapper.to_persistence(entity)
        await self.executor.add(model)

    async def save(self, entity: Assistant) -> None:
        model = AssistantMapper.to_persistence(entity)
        await self.executor.save(model)
