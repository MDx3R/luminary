from dataclasses import dataclass
from typing import Self
from uuid import UUID


@dataclass(frozen=True)
class AuthTokens:
    user_id: UUID
    access_token: str
    refresh_token: str

    @classmethod
    def create(cls, user_id: UUID, access_token: str, refresh_token: str) -> Self:
        return cls(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
        )
