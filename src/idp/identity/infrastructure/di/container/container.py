from typing import Any

from dependency_injector import containers, providers
from idp.identity.application.services.identity_service import IdentityService
from idp.identity.application.usecases.command.create_identity_use_case import (
    CreateIdentityUseCase,
)
from idp.identity.domain.factories.identity_factory import IdentityFactory
from idp.identity.infrastructure.database.postgres.sqlalchemy.repositories.identity_repository import (
    IdentityRepository,
)
from idp.identity.infrastructure.services.bcrypt.password_hasher import (
    BcryptPasswordHasher,
)


class IdentityContainer(containers.DeclarativeContainer):
    uuid_generator: providers.Dependency[Any] = providers.Dependency()
    query_executor: providers.Dependency[Any] = providers.Dependency()
    # NOTE: token_introspector is for semantics only, not used but needed for presentation layer
    token_introspector: providers.Dependency[Any] = providers.Dependency()

    identity_factory = providers.Singleton(IdentityFactory, uuid_generator)
    identity_repository = providers.Singleton(IdentityRepository, query_executor)

    password_hasher = providers.Singleton(BcryptPasswordHasher)

    identity_service = providers.Singleton(
        IdentityService,
        identity_repository=identity_repository,
        identity_factory=identity_factory,
        password_hasher=password_hasher,
    )
    create_identity_use_case = providers.Singleton(
        CreateIdentityUseCase, identity_service
    )
