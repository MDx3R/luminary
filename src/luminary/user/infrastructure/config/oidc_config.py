from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class OIDCConfig(BaseSettings):
    userinfo_url: HttpUrl = HttpUrl("http://zitadel.localhost/oidc/v1/userinfo")
    timeout_seconds: float = Field(default=5.0, gt=0)

    model_config = SettingsConfigDict(env_prefix="OIDC__", extra="ignore")
