from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.interfaces.chat_factory import ChatFactoryDTO, IChatFactory
from luminary.chat.domain.value_objects.chat_id import ChatId


class ChatFactory(IChatFactory):
    DEFAULT_CHAT_NAME: str = "Чат без имени"

    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator

    def create(self, data: ChatFactoryDTO) -> Chat:
        name = data.name
        if name is None:
            name = self.DEFAULT_CHAT_NAME

        return Chat.create(
            id=ChatId(self.uuid_generator.create()),
            owner_id=data.user_id,
            folder_id=data.folder_id,
            name=name,
            assistant_id=data.assisnant_id,
            settings=data.settings,
            created_at=self.clock.now(),
        )
