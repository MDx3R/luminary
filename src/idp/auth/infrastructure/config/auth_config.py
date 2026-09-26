from datetime import timedelta

from pydantic import BaseModel


class AuthConfig(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    issuer: str
    access_token_ttl: timedelta = timedelta(minutes=15)
    refresh_token_ttl: timedelta = timedelta(days=7)
