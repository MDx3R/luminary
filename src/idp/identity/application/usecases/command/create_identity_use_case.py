from uuid import UUID

from idp.identity.application.dtos.commands.create_identity_command import (
    CreateIdentityCommand,
)
from idp.identity.application.interfaces.services.identity_service import (
    IIdentityService,
)
from idp.identity.application.interfaces.usecases.command.create_identity_use_case import (
    ICreateIdentityUseCase,
)


class CreateIdentityUseCase(ICreateIdentityUseCase):
    def __init__(self, identity_service: IIdentityService) -> None:
        self.identity_service = identity_service

    async def execute(self, command: CreateIdentityCommand) -> UUID:
        return await self.identity_service.create_identity(command)
