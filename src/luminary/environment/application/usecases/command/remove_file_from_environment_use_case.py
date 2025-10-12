from luminary.environment.application.interfaces.repositories.environment_repository import (
    IEnvironmentRepository,
)
from luminary.environment.application.interfaces.usecases.command.remove_file_from_environment_use_case import (
    IRemoveFileFromEnvironmentUseCase,
    RemoveFileFromEnvironmentCommand,
)


class RemoveFileFromEnvironmentUseCase(IRemoveFileFromEnvironmentUseCase):
    def __init__(self, environment_repository: IEnvironmentRepository) -> None:
        self.environment_repository = environment_repository

    async def execute(self, command: RemoveFileFromEnvironmentCommand) -> None:
        environment = await self.environment_repository.get_by_id(
            command.environment_id
        )

        if environment.user_id != command.user_id:
            raise PermissionError

        if not environment.has_file(command.file_id):
            return

        environment.remove_file(command.file_id)
        await self.environment_repository.save(environment)
