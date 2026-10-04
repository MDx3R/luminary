from typing import Any

from dependency_injector import containers, providers

from luminary.user.application.usecases.resolve_user_use_case import ResolveUserUseCase
from luminary.user.infrastructure.database.postgres.sqlalchemy.repositories.user_repository import (
    UserRepository,
)


class UserContainer(containers.DeclarativeContainer):
    uuid_generator: providers.Dependency[Any] = providers.Dependency()
    query_executor: providers.Dependency[Any] = providers.Dependency()

    user_repository = providers.Singleton(UserRepository, query_executor)
    resolve_user_use_case = providers.Singleton(
        ResolveUserUseCase, user_repository, uuid_generator
    )
