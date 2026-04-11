from dataclasses import dataclass
from typing import Self

from idp.identity.domain.value_objects.identity_id import IdentityId
from idp.identity.domain.value_objects.password import Password
from idp.identity.domain.value_objects.username import Username


@dataclass
class Identity:
    id: IdentityId
    username: Username
    password: Password

    @classmethod
    def create(cls, id: IdentityId, username: str, password: str) -> Self:
        return cls(id=id, username=Username(username), password=Password(password))
