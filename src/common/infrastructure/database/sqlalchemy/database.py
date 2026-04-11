import logging
from typing import Self

from common.infrastructure.config.database_config import DatabaseConfig
from common.infrastructure.database.sqlalchemy.session_factory import MAKER
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.session import AsyncSession


class Database:
    def __init__(self, engine: AsyncEngine, logger: logging.Logger):
        self._engine = engine
        self._logger = logger
        self._create_session_maker()

    @classmethod
    def create(
        cls, config: DatabaseConfig, logger: logging.Logger | None = None
    ) -> Self:
        return cls(
            engine=cls.create_engine(config),
            logger=logger or logging.getLogger(),
        )

    @staticmethod
    def create_engine(config: DatabaseConfig) -> AsyncEngine:
        return create_async_engine(config.database_url, echo=False)

    def _create_session_maker(self) -> None:
        self._session_maker = async_sessionmaker[AsyncSession](
            bind=self._engine, expire_on_commit=False
        )

    def get_engine(self) -> AsyncEngine:
        return self._engine

    def get_session_maker(self) -> MAKER:
        return self._session_maker

    async def shutdown(self) -> None:
        self._logger.info("disposing database engine...")
        await self._engine.dispose()
        self._logger.info("database engine disposed gracefully")
