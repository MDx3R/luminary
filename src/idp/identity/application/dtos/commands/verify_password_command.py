from dataclasses import dataclass


@dataclass(frozen=True)
class VerifyPasswordCommand:
    username: str
    password: str
