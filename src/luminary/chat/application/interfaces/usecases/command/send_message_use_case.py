from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from common.domain.value_objects.datetime import DateTime


@dataclass(frozen=True)
class SendMessageCommand:
    user_id: UUID
    environment_id: UUID
    message: str


@dataclass(frozen=True)
class MessageDTO:
    message_id: UUID
    response: str
    model_name: str
    cost: Decimal
    created_at: DateTime


class ISendMessageUseCase(ABC):
    @abstractmethod
    async def execute(self, command: SendMessageCommand) -> MessageDTO: ...
