"""Deployment meta configuration."""

from pydantic import BaseModel


class DeploymentMeta(BaseModel):
    """Deployment meta configuration."""

    external_url: str
