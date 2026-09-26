from dataclasses import dataclass


@dataclass(frozen=True)
class LoginCommand:
    username: str
    password: str
