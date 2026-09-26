from abc import ABC, abstractmethod
from uuid import UUID

from idp.auth.application.dtos.models.auth_tokens import AuthTokens


class ITokenIssuer(ABC):
    @abstractmethod
    async def issue_tokens(self, identity_id: UUID) -> AuthTokens: ...


class ITokenRefresher(ABC):
    @abstractmethod
    async def refresh_tokens(self, refresh_token: str) -> AuthTokens: ...


class ITokenRevoker(ABC):
    @abstractmethod
    async def revoke_refresh_token(self, refresh_token: str) -> None: ...
