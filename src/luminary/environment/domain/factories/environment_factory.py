from uuid import UUID

from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.environment.domain.entity.environment import Environment
from luminary.environment.domain.interfaces.environment_factory import (
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
            self.uuid_generator.create(),
            name,
            description,
            user_id,
            model_id,
            assistant_id,
            self.clock.now(),
        )
