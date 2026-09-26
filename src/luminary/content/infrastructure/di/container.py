"""Lecturer bounded context DI container."""

from typing import Any

from dependency_injector import containers, providers

from luminary.content.application.services.content_service import ContentService
from luminary.content.domain.factories.content_factory import ContentFactory
from luminary.content.infrastructure.database.postgres.sqlalchemy.repositories.content_repository import (
    ContentRepository,
)
from luminary.content.infrastructure.storage.minio.repositories.content_storage import (
    MinioContentStorage,
)


class ContentContainer(containers.DeclarativeContainer):
    """Dependency injection container for source bounded context."""

    # Explicit dependency declarations
    bucket_name: providers.Dependency[Any] = providers.Dependency()

    clock: providers.Dependency[Any] = providers.Dependency()
    uuid_generator: providers.Dependency[Any] = providers.Dependency()
    query_executor: providers.Dependency[Any] = providers.Dependency()

    storage: providers.Dependency[Any] = providers.Dependency()

    file_content_extractor: providers.Dependency[Any] = providers.Dependency()

    # Domain services
    content_factory = providers.Singleton(
        ContentFactory, clock=clock, uuid_generator=uuid_generator
    )

    # Write repository
    content_repository = providers.Singleton(ContentRepository, query_executor)

    # Storage
    content_storage = providers.Singleton(
        MinioContentStorage, client=storage, bucket_name=bucket_name
    )

    # Services
    content_service = providers.Singleton(
        ContentService,
        bucket_name=bucket_name,
        content_factory=content_factory,
        file_content_extractor=file_content_extractor,
        content_repository=content_repository,
        content_storage=content_storage,
    )
