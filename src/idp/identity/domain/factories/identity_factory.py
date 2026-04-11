from common.domain.interfaces.uuid_generator import IUUIDGenerator
from idp.identity.domain.entity.identity import Identity
from idp.identity.domain.interfaces.identity_factory import IIdentityFactory
from idp.identity.domain.value_objects.identity_id import IdentityId


class IdentityFactory(IIdentityFactory):
    def __init__(self, uuid_generator: IUUIDGenerator) -> None:
        self.uuid_generator = uuid_generator

    def create(self, username: str, password: str) -> Identity:
        return Identity.create(
            IdentityId(self.uuid_generator.create()), username, password
        )
