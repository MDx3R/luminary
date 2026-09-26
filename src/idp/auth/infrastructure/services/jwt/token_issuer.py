from datetime import timedelta
from typing import Any
from uuid import UUID

from common.domain.interfaces.clock import IClock
from common.domain.interfaces.token_generator import ITokenGenerator
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from common.domain.value_objects.datetime import DateTime
from idp.auth.application.dtos.models.auth_tokens import AuthTokens
from idp.auth.application.interfaces.repositories.token_repository import (
    IRefreshTokenRepository,
)
from idp.auth.application.interfaces.services.token_service import ITokenIssuer
from idp.auth.domain.entity.token import Token, TokenTypeEnum
from idp.auth.infrastructure.config.auth_config import AuthConfig
from idp.auth.infrastructure.services.jwt.claims import TokenClaims
from jose import jwt


class JWTTokenIssuer(ITokenIssuer):
    def __init__(
        self,
        clock: IClock,
        config: AuthConfig,
        token_generator: ITokenGenerator,
        uuid_generator: IUUIDGenerator,
        refresh_token_repository: IRefreshTokenRepository,
    ) -> None:
        self.config = config
        self.clock = clock
        self.token_generator = token_generator
        self.uuid_generator = uuid_generator
        self.refresh_token_repository = refresh_token_repository

    async def issue_tokens(self, identity_id: UUID) -> AuthTokens:
        access = self.issue_access_token(identity_id)
        refresh = self.issue_refresh_token(identity_id)

        await self.refresh_token_repository.add(refresh)

        return AuthTokens.create(identity_id, access.value, refresh.value)

    def issue_access_token(self, identity_id: UUID) -> Token:
        issued_at = self.clock.now()
        expires_at = self.expires_at(issued_at, self.config.access_token_ttl)

        claims = TokenClaims.create(
            identity_id, self.config.issuer, issued_at.value, expires_at.value
        )
        token_str = self.create_jwt_token(claims)

        return Token.create(
            token_id=self.uuid_generator.create(),
            identity_id=identity_id,
            value=token_str,
            token_type=TokenTypeEnum.ACCESS,
            issued_at=issued_at,
            expires_at=expires_at,
        )

    def issue_refresh_token(self, user_id: UUID) -> Token:
        issued_at = self.clock.now()
        expires_at = self.expires_at(issued_at, self.config.refresh_token_ttl)

        token_value = self.token_generator.secure(64)

        refresh_token = Token.create(
            token_id=self.uuid_generator.create(),
            identity_id=user_id,
            value=token_value,
            token_type=TokenTypeEnum.REFRESH,
            issued_at=issued_at,
            expires_at=expires_at,
        )

        return refresh_token

    def create_jwt_token(self, claims: TokenClaims) -> str:
        payload: dict[str, Any] = {
            "sub": str(claims.sub),
            "iss": claims.iss,
            "iat": int(claims.iat.timestamp()),
            "exp": int(claims.exp.timestamp()),
        }
        return jwt.encode(
            payload,
            self.config.secret_key,
            algorithm=self.config.algorithm,
        )

    def expires_at(self, issued_at: DateTime, ttl: timedelta) -> DateTime:
        return issued_at + ttl
