from luminary.environment.application.interfaces.repositories.environment_repository import (
    IEnvironmentRepository,
)
from luminary.environment.application.interfaces.usecases.command.add_file_to_environment_use_case import (
    AddFileToEnvironmentCommand,
    IAddFileToEnvironmentUseCase,
)
from luminary.file.application.interfaces.respositories.file_repository import (
    IFileRepository,
)


class AddFileToEnvironmentUseCase(IAddFileToEnvironmentUseCase):
    def __init__(
        self,
        environment_repository: IEnvironmentRepository,
        file_repository: IFileRepository,
    ) -> None:
        self.environment_repository = environment_repository
        self.file_repository = file_repository

    async def execute(self, command: AddFileToEnvironmentCommand) -> None:
        file = await self.file_repository.get_by_id(command.file_id)
        environment = await self.environment_repository.get_by_id(
            command.environment_id
        )

        if file.user_id != command.user_id or environment.user_id != command.user_id:
            raise PermissionError

        environment.add_file(command.file_id)

        await self.environment_repository.save(environment)
