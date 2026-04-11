from dataclasses import asdict
from typing import Annotated

from common.presentation.http.fastapi.cbv import cbv
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from idp.auth.application.dtos.commands.login_command import LoginCommand
from idp.auth.application.dtos.commands.logout_command import LogoutCommand
from idp.auth.application.dtos.commands.refresh_token_command import (
    RefreshTokenCommand,
)
from idp.auth.application.interfaces.usecases.command.login_use_case import (
    ILoginUseCase,
)
from idp.auth.application.interfaces.usecases.command.logout_use_case import (
    ILogoutUseCase,
)
from idp.auth.application.interfaces.usecases.command.refresh_token_use_case import (
    IRefreshTokenUseCase,
)
from idp.auth.presentation.http.dto.request import RefreshTokenRequest
from idp.auth.presentation.http.dto.response import AuthTokensResponse
from idp.identity.application.exceptions import (
    InvalidPasswordError,
    InvalidUsernameError,
)
from idp.identity.presentation.http.fastapi.auth import (
    get_token,
    require_authenticated,
    require_unauthenticated,
)


auth_router = APIRouter()


@cbv(auth_router)
class AuthController:
    login_use_case: ILoginUseCase = Depends()
    logout_use_case: ILogoutUseCase = Depends()
    refresh_token_use_case: IRefreshTokenUseCase = Depends()

    @auth_router.post("/login", dependencies=[Depends(require_unauthenticated)])
    async def login(
        self, form: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> AuthTokensResponse:
        try:
            result = await self.login_use_case.execute(
                LoginCommand(username=form.username, password=form.password)
            )
            return AuthTokensResponse(**asdict(result))
        except (InvalidPasswordError, InvalidUsernameError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "InvalidUsernameOrPasswordError",
                    "message": "Username or password are incorrect.",
                },
            ) from exc

    @auth_router.post(
        "/logout",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(require_authenticated)],
    )
    async def logout(self, token: Annotated[str, Depends(get_token)]) -> None:
        await self.logout_use_case.execute(LogoutCommand(refresh_token=token))

    @auth_router.post("/refresh", dependencies=[Depends(require_unauthenticated)])
    async def refresh(
        self, form: Annotated[RefreshTokenRequest, Form()]
    ) -> AuthTokensResponse:
        result = await self.refresh_token_use_case.execute(
            RefreshTokenCommand(form.refresh_token)
        )
        return AuthTokensResponse(**asdict(result))
