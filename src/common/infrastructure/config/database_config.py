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


class MongoConfig(BaseModel):
    mongo_db: str
    mongo_user: str | None = None
    mongo_pass: str | None = None
    mongo_host: str
    mongo_port: int
    use_srv: bool = False

    @property
    def database_url(self) -> str:
        return DatabaseConfig(
            db_name=self.mongo_db,
            db_user=self.mongo_user,
            db_pass=self.mongo_pass,
            db_host=self.mongo_host,
            db_port=self.mongo_port,
            db_driver=DatabaseDriverEnum.MONGODB,
            db_extension=DatabaseExtensionEnum.SRV if self.use_srv else None,
        ).database_url
