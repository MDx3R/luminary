from idp.auth.application.dtos.commands.login_command import LoginCommand
from idp.auth.application.dtos.models.auth_tokens import AuthTokens
from idp.auth.application.interfaces.services.token_service import ITokenIssuer
from idp.auth.application.interfaces.usecases.command.login_use_case import (
    ILoginUseCase,
)
from idp.identity.application.dtos.commands.verify_password_command import (
    VerifyPasswordCommand,
)
from idp.identity.application.interfaces.services.identity_service import (
    IIdentityService,
)


class LoginUseCase(ILoginUseCase):
    def __init__(
        self,
        identity_service: IIdentityService,
        token_issuer: ITokenIssuer,
    ) -> None:
        self.identity_service = identity_service
        self.token_issuer = token_issuer

    async def execute(self, command: LoginCommand) -> AuthTokens:
        identity_id = await self.identity_service.verify_password(
            VerifyPasswordCommand(command.username, command.password)
        )
        return await self.token_issuer.issue_tokens(identity_id)
