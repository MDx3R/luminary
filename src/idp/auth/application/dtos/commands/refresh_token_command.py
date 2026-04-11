from dataclasses import dataclass


@dataclass(frozen=True)
class RefreshTokenCommand:
    refresh_token: str
