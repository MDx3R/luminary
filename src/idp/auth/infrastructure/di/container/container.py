from typing import Any

from dependency_injector import containers, providers
from idp.auth.application.repositories.descriptor_repository import (
    IdentityDescriptorRepository,
)
from idp.auth.application.usecases.command.login_use_case import LoginUseCase
from idp.auth.application.usecases.command.logout_use_case import LogoutUseCase
from idp.auth.application.usecases.command.refresh_token_use_case import (
    RefreshTokenUseCase,
)
from idp.auth.infrastructure.database.postgres.sqlalchemy.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from idp.auth.infrastructure.services.jwt.token_introspector import JWTTokenIntrospector
from idp.auth.infrastructure.services.jwt.token_issuer import JWTTokenIssuer
from idp.auth.infrastructure.services.jwt.token_refresher import JWTTokenRefresher
from idp.auth.infrastructure.services.jwt.token_revoker import JWTTokenRevoker


class TokenContainer(containers.DeclarativeContainer):
    auth_config: providers.Dependency[Any] = providers.Dependency()

    clock: providers.Dependency[Any] = providers.Dependency()
    uuid_generator: providers.Dependency[Any] = providers.Dependency()
    token_generator: providers.Dependency[Any] = providers.Dependency()

    query_executor: providers.Dependency[Any] = providers.Dependency()
    identity_repository: providers.Dependency[Any] = providers.Dependency()

    refresh_token_repository = providers.Singleton(
        RefreshTokenRepository, query_executor
    )
    identity_descriptor_repository = providers.Singleton(
        IdentityDescriptorRepository, identity_repository
    )

    token_issuer = providers.Singleton(
        JWTTokenIssuer,
        config=auth_config,
        token_generator=token_generator,
        uuid_generator=uuid_generator,
        clock=clock,
        refresh_token_repository=refresh_token_repository,
    )
    token_revoker = providers.Singleton(
        JWTTokenRevoker,
        clock=clock,
        refresh_token_repository=refresh_token_repository,
    )
    token_refresher = providers.Singleton(
        JWTTokenRefresher,
        token_issuer=token_issuer,
        token_revoker=token_revoker,
        clock=clock,
        refresh_token_repository=refresh_token_repository,
    )
    token_introspector = providers.Singleton(
        JWTTokenIntrospector,
        config=auth_config,
        descriptor_repository=identity_descriptor_repository,
        clock=clock,
    )


class AuthContainer(containers.DeclarativeContainer):
    identity_service: providers.Dependency[Any] = providers.Dependency()

    token_issuer: providers.Dependency[Any] = providers.Dependency()
    token_revoker: providers.Dependency[Any] = providers.Dependency()
    token_refresher: providers.Dependency[Any] = providers.Dependency()

    login_use_case = providers.Singleton(
        LoginUseCase,
        identity_service=identity_service,
        token_issuer=token_issuer,
    )
    refresh_token_use_case = providers.Singleton(RefreshTokenUseCase, token_refresher)
    logout_use_case = providers.Singleton(LogoutUseCase, token_revoker)
