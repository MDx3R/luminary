from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ExternalProfile:
    subject: str
    name: str
    email: str


@dataclass(frozen=True)
class UserProfile:
    id: UUID
    name: str
    email: str
