from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assisnant import (
    Assistant,
    AssistantId,
    Instructions,
)
from luminary.assistant.domain.interfaces.assistant_factory import IAssistantFactory


class AssistantFactory(IAssistantFactory):
    # TODO: Remove as we fetch default settings from repo
    DEFAULT_PROMPT: str = "You are a helpful assistant"

    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator

    def create(
        self, user_id: UserId, name: str, description: str, prompt: str | None
    ) -> Assistant:
        return Assistant.create(
            id=AssistantId(self.uuid_generator.create()),
            owner_id=user_id,
            name=name,
            description=description,
            instructions=Instructions(prompt or self.DEFAULT_PROMPT),
        )
