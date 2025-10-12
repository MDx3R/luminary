from uuid import UUID

from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.chat.domain.entity.message import ChatMessage
from luminary.chat.domain.enums import ChatMessageAuthor
from luminary.chat.domain.interfaces.message_factory import IMessageFactory


class MessageFactory(IMessageFactory):
    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator

    def create(
        self, chat_id: UUID, role: ChatMessageAuthor, content: str
    ) -> ChatMessage:
        return ChatMessage.create(
            self.uuid_generator.create(), chat_id, role, content, self.clock.now()
        )
