from typing import Annotated

from common.application.value_objects.descriptor import IdentityDescriptor
from fastapi import Depends, HTTPException, Request, status

from luminary.user.application.exceptions import (
    IdentityProviderUnavailableError,
    InvalidIdentityError,
)
from luminary.user.application.interfaces.resolve_user_use_case import (
    IResolveUserUseCase,
)


MAX_SUBJECT_LENGTH = 255


def get_proxy_identity(request: Request) -> tuple[str, str, str]:
    """Read headers overwritten by the only public ingress, never raw client data."""
    names = ("x-user-id", "x-username", "authorization")
    if any(len(request.headers.getlist(name)) != 1 for name in names):
        raise _unauthorized()
    subject, username, authorization = (request.headers[name] for name in names)
    _validate_profile_headers(subject, username)
    return subject, username, _get_bearer_token(authorization)


def _validate_profile_headers(subject: str, username: str) -> None:
    if (
        not subject.strip()
        or len(subject) > MAX_SUBJECT_LENGTH
        or subject != subject.strip()
        or not username.strip()
    ):
        raise _unauthorized()


def _get_bearer_token(authorization: str) -> str:
    scheme, separator, token = authorization.partition(" ")
    if (
        scheme.lower() != "bearer"
        or not separator
        or not token
        or any(char.isspace() for char in token)
    ):
        raise _unauthorized()
    return token


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_descriptor(
    identity: Annotated[tuple[str, str, str], Depends(get_proxy_identity)],
    resolve_user: Annotated[IResolveUserUseCase, Depends()],
) -> IdentityDescriptor:
    try:
        return await resolve_user.execute(*identity)
    except InvalidIdentityError as exc:
        raise _unauthorized() from exc
    except IdentityProviderUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Identity provider unavailable",
        ) from exc
