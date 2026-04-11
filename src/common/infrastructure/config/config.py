from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Self

from common.infrastructure.config.loader import MergeSettingsSource
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class RunEnvironment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"
    TEST = "test"


class Settings(ABC, BaseSettings):
    env: RunEnvironment = Field(default_factory=lambda: RunEnvironment.LOCAL)

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @abstractmethod
    def masked_dict(self) -> dict[str, Any]: ...

    @classmethod
    def load(cls) -> Self:
        return cls()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # init > env > dotenv > yaml  > secrets
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            MergeSettingsSource(settings_cls),
            file_secret_settings,
        )
