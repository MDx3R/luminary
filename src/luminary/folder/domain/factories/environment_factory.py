from uuid import UUID

from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.folder.domain.entity.environment import Environment
from luminary.folder.domain.interfaces.environment_factory import (
    IEnvironmentFactory,
)


class EnvironmentFactory(IEnvironmentFactory):
    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator

    def create(
        self,
        name: str,
        description: str | None,
        user_id: UUID,
        model_id: UUID,
        assistant_id: UUID,
    ) -> Environment:
        return Environment.create(
            environment_id=self.uuid_generator.create(),
            name=name,
            description=description,
            user_id=user_id,
            model_id=model_id,
            assistant_id=assistant_id,
            created_at=self.clock.now(),
        )
