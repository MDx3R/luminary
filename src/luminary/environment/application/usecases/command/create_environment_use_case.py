from uuid import UUID

from luminary.environment.application.interfaces.repositories.environment_repository import (
    IEnvironmentRepository,
)
from luminary.environment.application.interfaces.usecases.command.create_environment_use_case import (
    CreateEnvironmentCommand,
    ICreateEnvironmentUseCase,
)
from luminary.environment.domain.interfaces.environment_factory import (
    IEnvironmentFactory,
)


class CreateEnvironmentUseCase(ICreateEnvironmentUseCase):
    def __init__(
        self,
        environment_factory: IEnvironmentFactory,
        environment_repository: IEnvironmentRepository,
    ) -> None:
        self.environment_factory = environment_factory
        self.environment_repository = environment_repository

    async def execute(self, command: CreateEnvironmentCommand) -> UUID:
        environment = self.environment_factory.create(
            command.name,
            command.description,
            command.user_id,
            command.model_id,
            command.assistant_id,
        )

        await self.environment_repository.add(environment)
        return environment.environment_id
