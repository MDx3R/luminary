from typing import Annotated

from common.application.value_objects.descriptor import IdentityDescriptor
from common.presentation.http.fastapi.auth import get_descriptor
from fastapi import APIRouter, Depends

from luminary.user.presentation.http.dto.response import UserResponse


user_router = APIRouter()


@user_router.get("/me")
async def me(
    descriptor: Annotated[IdentityDescriptor, Depends(get_descriptor)],
) -> UserResponse:
    return UserResponse(
        id=descriptor.identity_id, name=descriptor.name, email=descriptor.email
    )
