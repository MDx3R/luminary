from uuid import UUID

from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.assistant.domain.entity.assisnant import Assistant, Instructions
from luminary.assistant.domain.interfaces.assistant_factory import IAssistantFactory


class AssistantFactory(IAssistantFactory):
    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator

    def create(
        self, user_id: UUID, name: str, description: str, prompt: str
    ) -> Assistant:
        return Assistant.create(
            assistant_id=self.uuid_generator.create(),
            user_id=user_id,
            name=name,
            description=description,
            instructions=Instructions(prompt),
        )
