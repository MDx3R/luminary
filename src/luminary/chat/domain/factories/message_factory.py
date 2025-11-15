from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.enums import Author, MessageStatus
from luminary.chat.domain.interfaces.message_factory import (
    IMessageFactory,
    MessageFactoryDTO,
)
from luminary.chat.domain.value_objects.message_id import MessageId


class MessageFactory(IMessageFactory):
    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator

    def create(self, data: MessageFactoryDTO) -> Message:
        if data.role == Author.ASSISTANT:
            status = MessageStatus.PENDING
        else:
            status = MessageStatus.COMPLETED

        return Message.create(
            id=MessageId(self.uuid_generator.create()),
            chat_id=data.chat_id,
            model_id=data.model_id,
            role=data.role,
            status=status,
            content=data.content,
            created_at=self.clock.now(),
        )
