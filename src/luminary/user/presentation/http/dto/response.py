from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
