from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from idp.auth.application.interfaces.repositories.token_repository import (
    IRefreshTokenRepository,
)
from idp.auth.domain.entity.token import Token
from idp.auth.infrastructure.database.postgres.sqlalchemy.mappers.token_mapper import (
    TokenMapper,
)
from idp.auth.infrastructure.database.postgres.sqlalchemy.models.token_base import (
    TokenBase,
)
from sqlalchemy import select, update


class RefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self, executor: QueryExecutor):
        self.executor = executor

    async def get(self, value: str) -> Token:
        stmt = select(TokenBase).where(TokenBase.value == value)
        result = await self.executor.execute_scalar_one(stmt)
        if not result:
            raise NotFoundError(value)
        return TokenMapper.to_domain(result)

    async def revoke(self, value: str) -> None:
        stmt = update(TokenBase).where(TokenBase.value == value).values(revoked=True)
        await self.executor.execute(stmt)

    async def add(self, token: Token) -> None:
        base = TokenMapper.to_persistence(token)
        await self.executor.add(base)
