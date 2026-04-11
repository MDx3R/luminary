from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class IdentityDescriptor:
    identity_id: UUID
    username: str
