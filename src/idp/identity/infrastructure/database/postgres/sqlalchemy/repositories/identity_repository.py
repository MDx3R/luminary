from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from idp.identity.application.exceptions import IdentityNotFoundError
from idp.identity.application.interfaces.repositories.identity_repository import (
    IIdentityRepository,
)
from idp.identity.domain.entity.identity import Identity
from idp.identity.domain.value_objects.identity_id import IdentityId
from idp.identity.infrastructure.database.postgres.sqlalchemy.mappers.identity_mapper import (
    IdentityMapper,
)
from idp.identity.infrastructure.database.postgres.sqlalchemy.models.identity_base import (
    IdentityBase,
)
from sqlalchemy import exists, select


class IdentityRepository(IIdentityRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, id: IdentityId) -> Identity:
        stmt = select(IdentityBase).where(IdentityBase.identity_id == id.value)
        identity = await self.executor.execute_scalar_one(stmt)
        if not identity:
            raise IdentityNotFoundError(id)
        return IdentityMapper.to_domain(identity)

    async def exists_by_username(self, username: str) -> bool:
        stmt = select(exists().where(IdentityBase.username == username))
        return await self.executor.execute_scalar(stmt)

    async def get_by_username(self, username: str) -> Identity:
        stmt = select(IdentityBase).where(IdentityBase.username == username)
        identity = await self.executor.execute_scalar_one(stmt)
        if not identity:
            raise IdentityNotFoundError(username)
        return IdentityMapper.to_domain(identity)

    async def add(self, entity: Identity) -> None:
        model = IdentityMapper.to_persistence(entity)
        await self.executor.add(model)
