"""Build the production auth sidecar without sending local secrets to Docker."""

import io
import tarfile
from contextlib import ExitStack
from pathlib import Path
from typing import Any

from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network


ROOT = Path(__file__).resolve().parents[3]


def auth_container(
    client: Any, stack: ExitStack, network: Network, issuer: str = "http://oidc:8080"
) -> DockerContainer:
    context = io.BytesIO()
    files = {
        "Dockerfile": (ROOT / "docker/Dockerfile.auth").read_bytes(),
        "cli/auth/main.py": (ROOT / "cli/auth/main.py").read_bytes(),
        "cli/auth/__init__.py": b"",
    }
    with tarfile.open(fileobj=context, mode="w") as archive:
        for name, content in files.items():
            entry = tarfile.TarInfo(name)
            entry.size = len(content)
            archive.addfile(entry, io.BytesIO(content))
    context.seek(0)
    image, _ = client.images.build(fileobj=context, custom_context=True, rm=True)
    # Docker may reuse this image between fixtures; do not remove shared cache.
    return (
        DockerContainer(image.id)
        .with_network(network)
        .with_network_aliases("auth-check")
        .with_env("ZITADEL_ISSUER", issuer)
        .with_env("ZITADEL_API_CLIENT_ID", "api-client")
        .with_env("ZITADEL_API_CLIENT_SECRET", "test-secret")
        .with_env("ZITADEL_PROJECT_ID", "project")
        .with_env("APP_ORIGIN", "http://localhost")
    )
