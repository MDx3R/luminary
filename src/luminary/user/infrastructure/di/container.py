from typing import Any

from dependency_injector import containers, providers

from luminary.user.application.usecases.resolve_user_use_case import ResolveUserUseCase
from luminary.user.infrastructure.database.postgres.sqlalchemy.repositories.user_repository import (
    UserRepository,
)
from luminary.user.infrastructure.services.zitadel_profile_provider import (
    ZitadelProfileProvider,
)


class UserContainer(containers.DeclarativeContainer):
    uuid_generator: providers.Dependency[Any] = providers.Dependency()
    query_executor: providers.Dependency[Any] = providers.Dependency()
    http_client: providers.Dependency[Any] = providers.Dependency()
    userinfo_url: providers.Dependency[Any] = providers.Dependency()

    user_repository = providers.Singleton(UserRepository, query_executor)
    profile_provider = providers.Singleton(
        ZitadelProfileProvider, http_client, userinfo_url
    )
    resolve_user_use_case = providers.Singleton(
        ResolveUserUseCase, profile_provider, user_repository, uuid_generator
    )
