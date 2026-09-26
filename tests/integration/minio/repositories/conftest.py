import logging
import os

import pytest
from minio import Minio
from testcontainers.minio import MinioContainer


os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"


_MINIO_ACCESS_KEY = "minioadmin"
_MINIO_SECRET_KEY = "minioadmin"


_LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def minio_container():
    try:
        with MinioContainer(
            access_key=_MINIO_ACCESS_KEY, secret_key=_MINIO_SECRET_KEY
        ) as container:
            yield container
    except:
        _LOGGER.info("If 502, try turning off VPN")
        raise


@pytest.fixture(scope="session")
def minio(minio_container: MinioContainer):
    host = minio_container.get_container_host_ip()
    port = minio_container.get_exposed_port(9000)
    client = Minio(
        endpoint=f"{host}:{port}",
        access_key=_MINIO_ACCESS_KEY,
        secret_key=_MINIO_SECRET_KEY,
        secure=False,
    )
    return client
