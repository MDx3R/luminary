import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

from src.common.infrastructure.config.database_config import (
    DatabaseConfig,
    DatabaseDriverEnum,
    DatabaseExtensionEnum,
)
from src.common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from src.common.infrastructure.database.sqlalchemy.models.base import Base
from src.common.infrastructure.database.sqlalchemy.session_factory import ISessionFactory
from src.common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork

from src.luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
)

os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"

__models__: list[type[Base]] = [ChatBase]

class StaticSessionFactory(ISessionFactory):
    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def create(self) -> AsyncSession:
        return self._session

USE_TESTCONTAINERS = False

if USE_TESTCONTAINERS:
    try:
        from testcontainers.postgres import PostgresContainer
        
        @pytest.fixture(scope="session")
        def pg_container():
            """testcontainers"""
            with PostgresContainer("postgres:17") as postgres:
                yield postgres

        @pytest.fixture(scope="session")
        def database_config(pg_container) -> DatabaseConfig:
            """Конфигурация БД из контейнера"""
            return DatabaseConfig(
                db_name=pg_container.dbname,
                db_user=pg_container.username,
                db_host=pg_container.get_container_host_ip(),
                db_port=pg_container.get_exposed_port(5432),
                db_pass=pg_container.password,
                db_driver=DatabaseDriverEnum.POSTGRESQL,
                db_extension=DatabaseExtensionEnum.ASYNCPG,
            )
            
    except ImportError:
        USE_TESTCONTAINERS = False
        print("testcontainers not available, using static database configuration")

if not USE_TESTCONTAINERS:
    @pytest.fixture(scope="session")
    def database_config() -> DatabaseConfig:
        """Статическая конфигурация БД"""
        return DatabaseConfig(
            db_name="luminary_test",
            db_user="postgres",
            db_host="localhost",
            db_port="5432",
            db_pass="5428",
            db_driver=DatabaseDriverEnum.POSTGRESQL,
            db_extension=DatabaseExtensionEnum.ASYNCPG,
        )

@pytest_asyncio.fixture(scope="session")
async def engine(database_config: DatabaseConfig) -> AsyncEngine:
    engine = create_async_engine(database_config.database_url, echo=False)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(autouse=True)
async def init(engine: AsyncEngine):
    meta = Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)

@pytest_asyncio.fixture
async def maker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(bind=engine, expire_on_commit=False)

@pytest_asyncio.fixture
async def session_factory(maker: async_sessionmaker):
    async with maker() as session:
        await session.begin_nested()
        yield StaticSessionFactory(session)
        await session.rollback()

@pytest.fixture
def uow(session_factory: ISessionFactory):
    return UnitOfWork(session_factory)

@pytest.fixture
def query_executor(uow: UnitOfWork):
    return QueryExecutor(uow)