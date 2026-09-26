from enum import Enum

from pydantic import BaseModel


class DatabaseDriverEnum(str, Enum):
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"


class DatabaseExtensionEnum(str, Enum):
    ASYNCPG = "asyncpg"
    SRV = "srv"


class DatabaseConfig(BaseModel):
    db_name: str
    db_user: str | None = None
    db_pass: str | None = None
    db_host: str
    db_port: int
    db_driver: DatabaseDriverEnum
    db_extension: DatabaseExtensionEnum | None = None

    @property
    def database_url(self) -> str:
        driver_str = self.db_driver.value
        if self.db_extension:
            driver_str += f"+{self.db_extension.value}"

        return (
            f"{driver_str}://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


class S3Config(BaseModel):
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str
    region: str | None = None
    secure: bool = False
