import httpx
from pydantic import BaseModel, Field, ValidationError

from luminary.user.application.dtos.profile import ExternalProfile
from luminary.user.application.exceptions import (
    IdentityProviderUnavailableError,
    InvalidIdentityError,
)
from luminary.user.application.interfaces.profile_provider import IProfileProvider


class UserInfoResponse(BaseModel):
    sub: str = Field(min_length=1, max_length=255, strict=True)
    name: str = Field(min_length=1, strict=True)
    email: str = Field(min_length=1, strict=True)


class ZitadelProfileProvider(IProfileProvider):
    def __init__(self, client: httpx.AsyncClient, userinfo_url: str) -> None:
        self.client = client
        self.userinfo_url = userinfo_url

    async def get_profile(self, access_token: str) -> ExternalProfile:
        try:
            response = await self.client.get(
                self.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except httpx.RequestError as exc:
            raise IdentityProviderUnavailableError() from exc
        if response.status_code in (401, 403):
            raise InvalidIdentityError() from None
        if response.status_code != httpx.codes.OK:
            raise IdentityProviderUnavailableError()
        try:
            profile = UserInfoResponse.model_validate(response.json())
        except (ValueError, ValidationError) as exc:
            raise IdentityProviderUnavailableError() from exc
        return ExternalProfile(profile.sub, profile.name, profile.email)
