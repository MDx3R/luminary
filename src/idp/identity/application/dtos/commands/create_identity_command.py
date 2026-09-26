from dataclasses import dataclass


@dataclass(frozen=True)
class CreateIdentityCommand:
    username: str
    password: str
