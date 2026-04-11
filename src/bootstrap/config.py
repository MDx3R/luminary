from typing import Any

from common.infrastructure.config.config import Settings
from common.infrastructure.config.database_config import DatabaseConfig, S3Config
from common.infrastructure.config.deployment_meta import DeploymentMeta
from common.infrastructure.config.llm_config import LLMConfig
from common.infrastructure.config.logger_config import LoggerConfig
from common.infrastructure.config.qdrant_config import QdrantConfig
from common.infrastructure.config.rabbit_config import RabbitMQConfig
from idp.auth.infrastructure.config.auth_config import AuthConfig


class AppConfig(Settings):
    auth: AuthConfig
    db: DatabaseConfig
    llm: LLMConfig
    logger: LoggerConfig
    s3: S3Config
    deploy: DeploymentMeta
    rabbit: RabbitMQConfig
    qdrant: QdrantConfig

    def masked_dict(self) -> dict[str, Any]:
        return self.model_dump(
            mode="json",
            exclude={
                "db": {"db_pass"},
                "auth": {"secret_key", "algorithm"},
                "llm": {"api_key"},
                "s3": {"secret_key"},
                "rabbit": {"rabbit_pass"},
                "qdrant": {"secret_key"},
            },
        )
