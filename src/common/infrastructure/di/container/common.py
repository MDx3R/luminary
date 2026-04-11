"""Common infrastructure DI container."""

from typing import Any

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from common.infrastructure.di.container.providers import provide_maker_session_factory
from common.infrastructure.queues.faststream.event_bus import FastStreamRabbitMQEventBus
from common.infrastructure.services.clock import SystemClock
from common.infrastructure.services.id_generator import UUID4Generator
from common.infrastructure.services.secrets_token_generator import SecretsTokenGenerator
from dependency_injector import containers, providers


class CommonContainer(containers.DeclarativeContainer):
    """Shared infrastructure dependencies for all bounded contexts."""

    config: providers.Dependency[Any] = providers.Dependency()
    logger: providers.Dependency[Any] = providers.Dependency()
    database: providers.Dependency[Any] = providers.Dependency()
    storage: providers.Dependency[Any] = providers.Dependency()
    broker: providers.Dependency[Any] = providers.Dependency()

    queue_name: providers.Dependency[Any] = providers.Dependency()

    clock = providers.Singleton(SystemClock)
    uuid_generator = providers.Singleton(UUID4Generator)
    token_generator = providers.Singleton(SecretsTokenGenerator)

    session_factory = providers.Singleton(provide_maker_session_factory, database)
    unit_of_work = providers.Singleton(UnitOfWork, session_factory)
    query_executor = providers.Singleton(QueryExecutor, unit_of_work)

    event_bus = providers.Singleton(
        FastStreamRabbitMQEventBus,
        broker=broker,
        uuid_generator=uuid_generator,
        prefix=queue_name,
    )
