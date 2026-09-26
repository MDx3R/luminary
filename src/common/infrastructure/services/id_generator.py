from uuid import UUID, uuid4

from common.domain.interfaces.uuid_generator import IUUIDGenerator


class UUID4Generator(IUUIDGenerator):
    def create(self) -> UUID:
        return uuid4()
