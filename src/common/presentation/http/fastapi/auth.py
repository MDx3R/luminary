import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
oauth2_scheme_no_error = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def is_authenticated(
    token: Annotated[str | None, Depends(oauth2_scheme_no_error)],
) -> bool:
    return token is not None


def require_authenticated(
    authenticated: Annotated[bool, Depends(is_authenticated)],
) -> None:
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )


def is_unauthenticated(
    authenticated: Annotated[bool, Depends(is_authenticated)],
) -> bool:
    return not authenticated


def require_unauthenticated(
    authenticated: Annotated[bool, Depends(is_authenticated)],
) -> None:
    if authenticated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are already logged in",
        )


def get_token(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    return token


async def get_descriptor(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> uuid.UUID:
    return uuid.uuid4()
