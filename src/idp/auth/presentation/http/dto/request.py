from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    grant_type: str = "refresh_token"
