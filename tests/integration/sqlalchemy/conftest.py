import os

import pytest
import pytest_asyncio
from common.infrastructure.config.database_config import (
    DatabaseConfig,
    DatabaseDriverEnum,
    DatabaseExtensionEnum,
)
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.models.base import Base
from common.infrastructure.database.sqlalchemy.session_factory import ISessionFactory
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from luminary.assistant.infrastructure.database.postgres.sqlalchemy.models.assistant_base import (
    AssistantBase,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.attachment_base import (
    AttachmentBase,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
    ChatSourceAssociation,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.message_base import (
    MessageBase,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderBase,
    FolderChatAssociation,
    FolderSourceAssociation,
)
from luminary.source.infrastructure.database.postgres.sqlalchemy.models.source_base import (
    FileSourceBase,
    LinkSourceBase,
    PageSourceBase,
    SourceBase,
)


os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"

# Needed for proper database configuration, e.g. fkeys and tables
__models__: list[type[Base]] = [
    SourceBase,
    FileSourceBase,
    LinkSourceBase,
    PageSourceBase,
    AssistantBase,
    ChatBase,
    ChatSourceAssociation,
    MessageBase,
    AttachmentBase,
    FolderBase,
    FolderChatAssociation,
    FolderSourceAssociation,
]


class StaticSessionFactory(ISessionFactory):
    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def create(self) -> AsyncSession:
        return self._session


@pytest.fixture(scope="session")
def pg_container():
    with PostgresContainer("postgres:17") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def database_config(pg_container: PostgresContainer) -> DatabaseConfig:
    return DatabaseConfig(
        db_name=pg_container.dbname,
        db_user=pg_container.username,
        db_host=pg_container.get_container_host_ip(),
        db_port=pg_container.get_exposed_port(5432),
        db_pass=pg_container.password,
        db_driver=DatabaseDriverEnum.POSTGRESQL,
        db_extension=DatabaseExtensionEnum.ASYNCPG,
    )


@pytest_asyncio.fixture
async def engine(database_config: DatabaseConfig):
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
async def maker(engine: AsyncEngine):
    return async_sessionmaker[AsyncSession](bind=engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def session_factory(maker: async_sessionmaker[AsyncSession]):
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
