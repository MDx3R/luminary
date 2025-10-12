from uuid import UUID

from pydantic import BaseModel


class IdentityResponse(BaseModel):
    id: UUID
    username: str
