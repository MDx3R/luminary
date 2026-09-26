from typing import Any
from uuid import UUID

from common.application.exceptions import NotFoundError, RepositoryError
from common.domain.interfaces.clock import IClock
from idp.auth.application.interfaces.repositories.descriptor_repository import (
    IIdentityDescriptorRepository,
)
from idp.auth.infrastructure.config.auth_config import AuthConfig
from idp.auth.infrastructure.services.jwt.claims import TokenClaims
from idp.identity.application.exceptions import InvalidTokenError, TokenExpiredError
from idp.identity.application.interfaces.services.token_intospector import (
    ITokenIntrospector,
)
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor
from jose import ExpiredSignatureError, JWTError, jwt


class JWTTokenIntrospector(ITokenIntrospector):
    def __init__(
        self,
        config: AuthConfig,
        clock: IClock,
        descriptor_repository: IIdentityDescriptorRepository,
    ) -> None:
        self.config = config
        self.clock = clock
        self.descriptor_repository = descriptor_repository

    async def extract_user(self, token: str) -> IdentityDescriptor:
        claims = self.decode(token)
        try:
            return await self.descriptor_repository.get_by_id(claims.identity_id)
        except NotFoundError as e:
            raise RepositoryError(
                f"decoded identity_id {claims.identity_id} is not found"
            ) from e

    async def is_token_valid(self, token: str) -> bool:
        try:
            await self.validate(token)
            return True
        except Exception:
            return False

    async def validate(self, token: str) -> UUID:
        return self.decode(token).identity_id

    def decode(self, token: str) -> TokenClaims:
        try:
            payload = jwt.decode(
                token,
                key=self.config.secret_key,
                algorithms=[self.config.algorithm],
                issuer=self.config.issuer,
                options={"require": ["exp", "iat", "sub"]},
            )

            return self._parse_claims(payload)

        except ExpiredSignatureError as e:
            raise TokenExpiredError from e
        except JWTError as e:
            raise InvalidTokenError from e

    def _parse_claims(self, payload: dict[str, Any]) -> TokenClaims:
        try:
            return TokenClaims(
                sub=UUID(payload["sub"]),
                iss=payload["iss"],
                iat=self.clock.from_timestamp(payload["iat"]).value,
                exp=self.clock.from_timestamp(payload["exp"]).value,
            )
        except Exception as e:
            raise InvalidTokenError("Malformed token claims") from e
