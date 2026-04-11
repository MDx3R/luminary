from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, field_validator


class LoggingLevelEnum(Enum):
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class LoggerConfig(BaseModel):
    level: LoggingLevelEnum = LoggingLevelEnum.INFO
    format: Literal["json", "text"] = "json"

    @field_validator("level", mode="before")
    @classmethod
    def parse_level(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return LoggingLevelEnum[v.upper()]
            except KeyError:
                raise ValueError(f"Invalid logging level: {v}") from None
        return v
