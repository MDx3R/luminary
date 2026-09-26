import asyncio
from logging.config import fileConfig

from alembic import context
from bootstrap.config import AppConfig
from bootstrap.utils import log_config
from common.infrastructure.database.sqlalchemy.database import Database
from common.infrastructure.database.sqlalchemy.models.base import Base
from common.infrastructure.logger.logging.logger_factory import LoggerFactory
from idp.auth.infrastructure.database.postgres.sqlalchemy.models.token_base import (
    TokenBase,
)
from idp.identity.infrastructure.database.postgres.sqlalchemy.models.identity_base import (
    IdentityBase,
)
from luminary_files.infrastructure.database.postgres.sqlalchemy.models.file_base import (
    FileBase,
)
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from luminary.assistant.infrastructure.database.postgres.sqlalchemy.models.assistant_base import (
    AssistantBase,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.attachment_base import (
    AttachmentBase,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.message_base import (
    MessageBase,
)
from luminary.content.infrastructure.database.postgres.sqlalchemy.models.content_base import (
    ContentBase,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderBase,
)
from luminary.source.infrastructure.database.postgres.sqlalchemy.models.source_base import (
    SourceBase,
)


# Needed for proper database configuration, e.g. fkeys and tables
__models__: list[type[Base]] = [
    SourceBase,
    ContentBase,
    FileBase,
    AssistantBase,
    FolderBase,
    ChatBase,
    MessageBase,
    AttachmentBase,
    IdentityBase,
    TokenBase,
]

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
cfg = AppConfig.load()

logger = LoggerFactory.create(__name__, cfg.env, cfg.logger)
log_config(logger, cfg)

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    database = Database.create(cfg.db, logger)
    connectable: AsyncEngine = database.get_engine()

    logger.info("running migrations online using AsyncEngine")

    async def do_run_migrations() -> None:
        async with connectable.connect() as conn:
            logger.info("connected to database")
            await conn.run_sync(sync_migrations)
            logger.info("migrations finished")

    def sync_migrations(sync_connection: Connection) -> None:
        context.configure(
            connection=sync_connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

    asyncio.run(do_run_migrations())
    logger.info("migration runner completed")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
