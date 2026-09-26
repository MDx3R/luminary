from common.application.exceptions import NotFoundError
from common.domain.interfaces.clock import IClock
from idp.auth.application.interfaces.repositories.token_repository import (
    IRefreshTokenRepository,
)
from idp.auth.application.interfaces.services.token_service import ITokenRevoker
from idp.identity.application.exceptions import InvalidTokenError


class JWTTokenRevoker(ITokenRevoker):
    def __init__(
        self, clock: IClock, refresh_token_repository: IRefreshTokenRepository
    ) -> None:
        self.clock = clock
        self.refresh_token_repository = refresh_token_repository

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        try:
            token = await self.refresh_token_repository.get(refresh_token)
        except NotFoundError as e:
            raise InvalidTokenError from e
        if token.is_expired(self.clock.now()):
            return
        if token.is_revoked():
            return

        await self.refresh_token_repository.revoke(refresh_token)
