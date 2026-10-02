import httpx
import pytest

from luminary.user.application.dtos.profile import ExternalProfile
from luminary.user.application.exceptions import (
    IdentityProviderUnavailableError,
    InvalidIdentityError,
)
from luminary.user.infrastructure.services.zitadel_profile_provider import (
    ZitadelProfileProvider,
)


USERINFO_URL = "https://identity.example.com/oidc/v1/userinfo"


@pytest.mark.asyncio
async def test_profile_comes_from_configured_provider():
    def handle(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == USERINFO_URL
        assert request.headers["Authorization"] == "Bearer access-token"
        return httpx.Response(
            200, json={"sub": "123", "name": "Jane Doe", "email": "jane@example.com"}
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        result = await ZitadelProfileProvider(client, USERINFO_URL).get_profile(
            "access-token"
        )

    assert result == ExternalProfile("123", "Jane Doe", "jane@example.com")


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [401, 403])
async def test_rejected_tokens_are_unauthorized(status_code: int):
    transport = httpx.MockTransport(lambda _: httpx.Response(status_code))
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(InvalidIdentityError):
            await ZitadelProfileProvider(client, USERINFO_URL).get_profile("invalid")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(500),
        httpx.Response(302, headers={"Location": "https://untrusted.example"}),
        httpx.Response(200, content="not json"),
        httpx.Response(200, json={"sub": "123"}),
        httpx.Response(200, json={"sub": 123, "name": "Jane", "email": "jane@test.io"}),
        httpx.Response(200, json={"sub": "", "name": "Jane", "email": "jane@test.io"}),
    ],
)
async def test_provider_errors_fail_closed(response: httpx.Response):
    transport = httpx.MockTransport(lambda _: response)
    async with httpx.AsyncClient(transport=transport, follow_redirects=False) as client:
        with pytest.raises(IdentityProviderUnavailableError):
            await ZitadelProfileProvider(client, USERINFO_URL).get_profile("token")


@pytest.mark.asyncio
async def test_provider_timeout_fails_closed():
    def handle(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(IdentityProviderUnavailableError):
            await ZitadelProfileProvider(client, USERINFO_URL).get_profile("token")
