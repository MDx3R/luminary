from uuid import UUID

from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.interfaces.chat_factory import IChatFactory


class ChatFactory(IChatFactory):
    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator

    def create(self, environment_id: UUID) -> Chat:
        return Chat.create(
            chat_id=self.uuid_generator.create(),
            environment_id=environment_id,
            created_at=self.clock.now(),
        )
