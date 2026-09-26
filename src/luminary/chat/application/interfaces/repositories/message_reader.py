from abc import ABC, abstractmethod
from collections.abc import Sequence

from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.value_objects.chat_id import ChatId


class IMessageReader(ABC):
    """Read-only interface for loading chat messages (e.g. for inference context)."""

    @abstractmethod
    async def get_chat_messages(
        self, chat_id: ChatId, *, limit: int | None = None
    ) -> Sequence[Message]: ...
