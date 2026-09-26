"""Lecturer bounded context DI container."""

from typing import Any

from dependency_injector import containers, providers

from luminary.source.application.handlers.source_created_handler import (
    SourceCreatedHandler,
)
from luminary.source.application.handlers.source_fetched_handler import (
    SourceFetchedHandler,
)
from luminary.source.application.policies.source_access_policy import SourceAccessPolicy
from luminary.source.application.repositories.source_repository import (
    EventBusSourceRepository,
)
from luminary.source.application.usecases.command.create_source_use_case import (
    CreateFileSourceUseCase,
    CreateLinkSourceUseCase,
    CreatePageSourceUseCase,
)
from luminary.source.application.usecases.command.delete_source_use_case import (
    DeleteSourceUseCase,
)
from luminary.source.application.usecases.command.update_source_use_case import (
    UpdateSourceUseCase,
)
from luminary.source.application.usecases.query.get_source_use_case import (
    GetSourceByIdUseCase,
)
from luminary.source.application.usecases.query.list_user_sources_use_case import (
    ListUserSourcesUseCase,
)
from luminary.source.domain.factories.source_factory import SourceFactory
from luminary.source.infrastructure.database.postgres.sqlalchemy.repositories.source_read_repository import (
    SourceReadRepository,
)
from luminary.source.infrastructure.database.postgres.sqlalchemy.repositories.source_repository import (
    SourceRepository,
)


class SourceContainer(containers.DeclarativeContainer):
    """Dependency injection container for source bounded context."""

    # Explicit dependency declarations
    clock: providers.Dependency[Any] = providers.Dependency()
    uuid_generator: providers.Dependency[Any] = providers.Dependency()
    query_executor: providers.Dependency[Any] = providers.Dependency()

    unit_of_work: providers.Dependency[Any] = providers.Dependency()
    event_bus: providers.Dependency[Any] = providers.Dependency()

    file_service: providers.Dependency[Any] = providers.Dependency()
    content_service: providers.Dependency[Any] = providers.Dependency()
    embedding_service: providers.Dependency[Any] = providers.Dependency()

    # Domain services
    source_factory = providers.Singleton(
        SourceFactory, clock=clock, uuid_generator=uuid_generator
    )

    # Write repository
    source_repository = providers.Singleton(SourceRepository, query_executor)
    source_read_repository = providers.Singleton(SourceReadRepository, query_executor)
    event_bus_source_repository = providers.Singleton(
        EventBusSourceRepository,
        uow=unit_of_work,
        event_bus=event_bus,
        repository=source_repository,
    )

    # Access policy
    source_access_policy = providers.Singleton(SourceAccessPolicy)

    # Write use cases
    create_file_source_use_case = providers.Singleton(
        CreateFileSourceUseCase,
        source_factory=source_factory,
        source_repository=event_bus_source_repository,
    )
    create_link_source_use_case = providers.Singleton(
        CreateLinkSourceUseCase,
        source_factory=source_factory,
        source_repository=event_bus_source_repository,
    )
    create_page_source_use_case = providers.Singleton(
        CreatePageSourceUseCase,
        source_factory=source_factory,
        source_repository=event_bus_source_repository,
        content_service=content_service,
    )

    update_source_use_case = providers.Singleton(
        UpdateSourceUseCase,
        repository=event_bus_source_repository,
        access_policy=source_access_policy,
    )

    delete_source_use_case = providers.Singleton(
        DeleteSourceUseCase,
        repository=event_bus_source_repository,
        access_policy=source_access_policy,
    )

    # Query use cases
    get_source_by_id_use_case = providers.Singleton(
        GetSourceByIdUseCase, read_repository=source_read_repository
    )
    list_user_sources_use_case = providers.Singleton(
        ListUserSourcesUseCase, read_repository=source_read_repository
    )

    source_created_handler = providers.Singleton(
        SourceCreatedHandler,
        clock=clock,
        source_repository=event_bus_source_repository,
        content_service=content_service,
        file_service=file_service,
    )
    source_fetched_handler = providers.Singleton(
        SourceFetchedHandler,
        clock=clock,
        source_repository=event_bus_source_repository,
        content_service=content_service,
        embedding_service=embedding_service,
    )
