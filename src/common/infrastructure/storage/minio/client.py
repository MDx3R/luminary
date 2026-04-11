from typing import Self

from common.infrastructure.config.database_config import S3Config
from minio import Minio


class MinioStorage:
    def __init__(self, client: Minio, config: S3Config):
        self._client = client
        self._bucket_name = config.bucket_name
        self._config = config

    @classmethod
    def create(cls, config: S3Config) -> Self:
        client = cls.create_client(config)
        return cls(client=client, config=config)

    @staticmethod
    def create_client(config: S3Config) -> Minio:
        return Minio(
            endpoint=config.endpoint_url,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=config.secure,
        )

    def get_config(self) -> S3Config:
        return self._config

    def get_client(self) -> Minio:
        return self._client

    def get_bucket_name(self) -> str:
        return self._bucket_name

    async def ensure_bucket(self, bucket_name: str | None = None) -> None:
        bucket_name = bucket_name or self._bucket_name
        if not self._client.bucket_exists(bucket_name):
            self._client.make_bucket(bucket_name)

    async def shutdown(self) -> None:
        """MinIO does not maintain a persistent connection."""
        pass
