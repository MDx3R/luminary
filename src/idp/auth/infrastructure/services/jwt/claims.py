from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID


@dataclass(frozen=True)
class TokenClaims:
    sub: UUID
    iss: str
    iat: datetime
    exp: datetime

    @property
    def identity_id(self) -> UUID:
        return self.sub

    @classmethod
    def create(
        cls,
        identity_id: UUID,
        issuer: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> Self:
        return cls(sub=identity_id, iss=issuer, iat=issued_at, exp=expires_at)
