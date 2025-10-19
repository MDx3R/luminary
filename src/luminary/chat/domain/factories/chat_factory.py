from uuid import UUID

from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.chat.domain.entity.chat import Chat, ChatSettings
from luminary.chat.domain.interfaces.chat_factory import IChatFactory


class ChatFactory(IChatFactory):
    DEFAULT_CHAT_NAME: str = "Чат без имени"

    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator

    def create(
        self,
        user_id: UUID,
        folder_id: UUID | None,
        name: str | None,
        settings: ChatSettings,
    ) -> Chat:
        if name is None:
            name = self.DEFAULT_CHAT_NAME

        return Chat.create(
            chat_id=self.uuid_generator.create(),
            folder_id=folder_id,
            user_id=user_id,
            name=name,
            settings=settings,
            created_at=self.clock.now(),
        )
