from typing import Annotated

from common.application.value_objects.descriptor import IdentityDescriptor
from fastapi import Depends, HTTPException, Request, status

from luminary.user.application.dtos.profile import ExternalProfile
from luminary.user.application.interfaces.resolve_user_use_case import (
    IResolveUserUseCase,
)


MAX_SUBJECT_LENGTH = 255


def get_proxy_identity(request: Request) -> tuple[ExternalProfile, str]:
    """Read headers overwritten by the only public ingress, never raw client data."""
    names = ("x-user-id", "x-user-name", "x-email")
    if any(len(request.headers.getlist(name)) != 1 for name in names):
        raise _unauthorized()
    subject, name, email = (_decode_header(request.headers[name]) for name in names)
    if any(not value.strip() for value in (subject, name, email)):
        raise _unauthorized()
    if len(request.headers.getlist("x-username")) > 1:
        raise _unauthorized()
    username = _decode_header(request.headers.get("x-username", "")).strip()
    _validate_subject(subject)
    return ExternalProfile(subject, name, email), username


def _decode_header(value: str) -> str:
    # ASGI exposes raw header bytes as Latin-1; oauth2-proxy sends UTF-8 claims.
    try:
        return value.encode("latin-1").decode("utf-8")
    except UnicodeError as exc:
        raise _unauthorized() from exc


def _validate_subject(subject: str) -> None:
    if len(subject) > MAX_SUBJECT_LENGTH or subject != subject.strip():
        raise _unauthorized()


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )


async def get_descriptor(
    identity: Annotated[tuple[ExternalProfile, str], Depends(get_proxy_identity)],
    resolve_user: Annotated[IResolveUserUseCase, Depends()],
) -> IdentityDescriptor:
    return await resolve_user.execute(*identity)
