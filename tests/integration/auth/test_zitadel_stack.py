"""Opt-in smoke test of the real identity services, with disposable databases."""

import io
import os
import re
import secrets
import tarfile
from contextlib import ExitStack
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
import yaml
from fastapi import status
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import HealthcheckWaitStrategy
from testcontainers.core.waiting_utils import wait_for_logs


ROOT = Path(__file__).resolve().parents[3]
pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_ZITADEL_SMOKE") != "1",
    reason="Set RUN_ZITADEL_SMOKE=1 to pull and run the real Zitadel stack",
)


def interpolate(value: Any, settings: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        name, modifier, fallback = match.group(1, 2, 3)
        if settings.get(name):
            return settings[name]
        if modifier == ":-":
            return fallback
        raise ValueError(f"Missing smoke-test setting: {name}")

    if isinstance(value, bool):
        return str(value).lower()
    return re.sub(r"\$\{([A-Z0-9_]+)(:-|:\?)?([^}]*)\}", replace, str(value))


def service_container(service: dict[str, Any], settings: dict[str, str], network):
    container = DockerContainer(interpolate(service["image"], settings)).with_network(
        network
    )
    for name, value in service.get("environment", {}).items():
        container.with_env(name, interpolate(value, settings))
    if "command" in service:
        container.with_command(service["command"])
    if "healthcheck" in service:
        container.with_kwargs(
            healthcheck={
                "test": service["healthcheck"]["test"],
                "interval": 1_000_000_000,
                "timeout": 5_000_000_000,
                "retries": 30,
            }
        )
        container.waiting_for(HealthcheckWaitStrategy().with_startup_timeout(60))
    return container


def assert_success(container, settings: dict[str, str]) -> None:
    result = container.get_wrapped_container().wait(timeout=60)
    logs = b"\n".join(container.get_logs()).decode()
    for value in settings.values():
        logs = logs.replace(value, "[redacted]")
    assert result["StatusCode"] == 0, logs[-5000:]


def proxy_image(client, stack: ExitStack, image_name: str):
    """Copy the actual config without requiring Docker Desktop filesystem mounts."""
    context = io.BytesIO()
    files = {
        "Dockerfile": f"FROM {image_name}\nCOPY proxy.cfg /etc/oauth2-proxy.cfg\n".encode(),
        "proxy.cfg": (ROOT / "oauth2-proxy/oauth2-proxy.cfg").read_bytes(),
    }
    with tarfile.open(fileobj=context, mode="w") as archive:
        for name, content in files.items():
            entry = tarfile.TarInfo(name)
            entry.size = len(content)
            archive.addfile(entry, io.BytesIO(content))
    context.seek(0)
    image, _ = client.images.build(fileobj=context, custom_context=True, rm=True)
    stack.callback(client.images.remove, image.id)
    return image.id


def test_real_zitadel_discovery_login_and_proxy_boundary():
    services = yaml.safe_load((ROOT / "docker-compose.yaml").read_text())["services"]
    settings = {
        "ZITADEL_MASTERKEY": secrets.token_hex(16),
        "ZITADEL_DB_PASSWORD": secrets.token_urlsafe(24),
        "ZITADEL_DB_ADMIN_PASSWORD": secrets.token_urlsafe(24),
        "ZITADEL_ADMIN_PASSWORD": secrets.token_urlsafe(24) + "aA1!",
        "ZITADEL_LOGIN_COOKIE_SECRET": secrets.token_urlsafe(32),
        "OAUTH2_PROXY_COOKIE_SECRET": secrets.token_urlsafe(32),
        "ZITADEL_DOMAIN": "zitadel.localhost",
        "APP_DOMAIN": "localhost",
        "APP_ORIGIN": "http://localhost",
    }
    with Network() as network, ExitStack() as stack:
        db = service_container(
            services["zitadel-db"], settings, network
        ).with_network_aliases("zitadel-db")
        stack.enter_context(db)
        wait_for_logs(db, "database system is ready to accept connections", timeout=30)

        init = service_container(services["zitadel-init"], settings, network)
        stack.enter_context(init)
        assert_success(init, settings)

        setup = service_container(services["zitadel-setup"], settings, network)
        volume = db.get_wrapped_container().client.volumes.create()
        stack.callback(volume.remove)
        setup.with_kwargs(user="0").with_volume_mapping(
            volume.name, "/zitadel/bootstrap", "rw"
        )
        stack.enter_context(setup)
        assert_success(setup, settings)

        api = service_container(
            services["zitadel-api"], settings, network
        ).with_network_aliases("zitadel-api")
        stack.enter_context(api)

        login = service_container(
            services["zitadel-login"], settings, network
        ).with_network_aliases("zitadel-login")
        login.with_kwargs(user="0").with_volume_mapping(
            volume.name, "/zitadel/bootstrap", "ro"
        )
        stack.enter_context(login)

        nginx = service_container(services["nginx"], settings, network)
        nginx.with_network_aliases("zitadel.localhost").with_exposed_ports(80)
        nginx.with_env(
            "NGINX_ENVSUBST_FILTER", "^(APP_DOMAIN|APP_ORIGIN|ZITADEL_DOMAIN)$"
        )
        nginx.with_env(
            "NGINX_TEST_TEMPLATE", (ROOT / "nginx/nginx.conf.template").read_text()
        )
        nginx.with_command(
            [
                "sh",
                "-c",
                "mkdir -p /etc/nginx/templates; "
                "printf '%s' \"$NGINX_TEST_TEMPLATE\" > /etc/nginx/templates/nginx.conf.template; "
                "exec /docker-entrypoint.sh nginx -g 'daemon off;'",
            ]
        )
        stack.enter_context(nginx)
        wait_for_logs(nginx, "start worker processes", timeout=30)
        settings["OAUTH2_PROXY_CLIENT_ID"] = "smoke-client"
        settings["OAUTH2_PROXY_CLIENT_SECRET"] = secrets.token_urlsafe(32)
        proxy_service = dict(services["oauth2-proxy"])
        proxy_service["image"] = proxy_image(
            db.get_wrapped_container().client, stack, proxy_service["image"]
        )
        proxy = service_container(
            proxy_service, settings, network
        ).with_network_aliases("oauth2-proxy")
        stack.enter_context(proxy)
        wait_for_logs(proxy, "OAuthProxy configured", timeout=30, raise_on_exit=True)
        base_url = (
            f"http://{nginx.get_container_host_ip()}:{nginx.get_exposed_port(80)}"
        )
        with httpx.Client(base_url=base_url, trust_env=False, timeout=10) as client:
            assert_identity_endpoints(client)
            assert_proxy_boundary(client)


def assert_identity_endpoints(client: httpx.Client) -> None:
    discovery = client.get(
        "/.well-known/openid-configuration", headers={"Host": "zitadel.localhost"}
    )
    assert discovery.status_code == status.HTTP_200_OK
    assert discovery.json()["issuer"] == "http://zitadel.localhost"
    assert (
        "client_secret_basic"
        in discovery.json()["token_endpoint_auth_methods_supported"]
    )
    response = client.get("/ui/v2/login/healthy", headers={"Host": "zitadel.localhost"})
    assert response.status_code == status.HTTP_200_OK


def assert_proxy_boundary(client: httpx.Client) -> None:
    unauthorized = client.get(
        "/users/me",
        headers={
            "Host": "localhost",
            "X-User-Id": "forged",
            "Authorization": "Bearer forged",
        },
    )
    assert unauthorized.status_code == status.HTTP_401_UNAUTHORIZED
    login_redirect = client.get("/oauth2/start", headers={"Host": "localhost"})
    assert login_redirect.status_code == status.HTTP_302_FOUND
    location = urlsplit(login_redirect.headers["Location"])
    assert location.hostname == "zitadel.localhost"
    parameters = parse_qs(location.query)
    assert parameters["response_type"] == ["code"]
    assert parameters["code_challenge_method"] == ["S256"]
    assert parameters["redirect_uri"] == ["http://localhost/oauth2/callback"]
