from uuid import UUID

from pydantic import BaseModel


class AuthTokensResponse(BaseModel):
    user_id: UUID
    access_token: str
    refresh_token: str
