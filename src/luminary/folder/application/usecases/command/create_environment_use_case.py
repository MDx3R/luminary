from uuid import UUID

from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.interfaces.chat_factory import IChatFactory
from luminary.folder.application.interfaces.repositories.environment_repository import (
    IEnvironmentRepository,
)
from luminary.folder.application.interfaces.usecases.command.create_environment_use_case import (
    CreateEnvironmentCommand,
    ICreateEnvironmentUseCase,
)
from luminary.folder.domain.interfaces.environment_factory import (
    IEnvironmentFactory,
)


class CreateEnvironmentUseCase(ICreateEnvironmentUseCase):
    def __init__(
        self,
        uow: IUnitOfWork,
        environment_factory: IEnvironmentFactory,
        chat_factory: IChatFactory,
        environment_repository: IEnvironmentRepository,
        chat_repository: IChatRepository,
    ) -> None:
        self.uow = uow
        self.environment_factory = environment_factory
        self.chat_factory = chat_factory
        self.environment_repository = environment_repository
        self.chat_repository = chat_repository

    async def execute(self, command: CreateEnvironmentCommand) -> UUID:
        environment = self.environment_factory.create(
            command.name,
            command.description,
            command.user_id,
            command.model_id,
            command.assistant_id,
        )
        chat = self.chat_factory.create(environment.environment_id)

        async with self.uow:
            await self.environment_repository.add(environment)
            await self.chat_repository.add(chat)

        return environment.environment_id
