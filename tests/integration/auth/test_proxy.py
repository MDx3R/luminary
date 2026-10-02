from pathlib import Path

import httpx
import pytest
import yaml
from fastapi import status
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs


ROOT = Path(__file__).resolve().parents[3]
FORGED_HEADERS = {
    "Host": "localhost",
    "X-User-Id": "victim",
    "X-Username": "victim",
    "Authorization": "Bearer forged-token",
    "X-Auth-Request-User": "victim",
    "X-Forwarded-User": "victim",
}


@pytest.fixture(scope="module")
def proxy_url():
    with Network() as network:
        stub = (
            DockerContainer("python:3.12-alpine")
            .with_network(network)
            .with_network_aliases("app", "oauth2-proxy")
            .with_command(
                ["python", "-c", Path(__file__).with_name("proxy_stub.py").read_text()]
            )
        )
        nginx = (
            DockerContainer("nginx:1.28-alpine")
            .with_network(network)
            .with_exposed_ports(80)
            .with_env("APP_DOMAIN", "localhost")
            .with_env("APP_ORIGIN", "http://localhost")
            .with_env("ZITADEL_DOMAIN", "zitadel.localhost")
            .with_env("NGINX_ENVSUBST_OUTPUT_DIR", "/etc/nginx")
            .with_env(
                "NGINX_ENVSUBST_FILTER", "^(APP_DOMAIN|APP_ORIGIN|ZITADEL_DOMAIN)$"
            )
            .with_env(
                "NGINX_TEST_TEMPLATE", (ROOT / "nginx/nginx.conf.template").read_text()
            )
            .with_command(
                [
                    "sh",
                    "-c",
                    "mkdir -p /etc/nginx/templates; "
                    "printf '%s' \"$NGINX_TEST_TEMPLATE\" > /etc/nginx/templates/nginx.conf.template; "
                    "exec /docker-entrypoint.sh nginx -g 'daemon off;'",
                ]
            )
        )
        with stub, nginx:
            wait_for_logs(stub, "stub ready")
            wait_for_logs(nginx, "start worker processes")
            yield f"http://{nginx.get_container_host_ip()}:{nginx.get_exposed_port(80)}"


@pytest.mark.parametrize("path", ["/users/me", "/api/v1/chats", "/docs"])
def test_proxy_rejects_forged_identity_without_session(proxy_url, path: str):
    response = httpx.get(proxy_url + path, headers=FORGED_HEADERS, trust_env=False)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_proxy_overwrites_client_identity(proxy_url):
    response = httpx.get(
        proxy_url + "/users/me",
        headers={**FORGED_HEADERS, "Cookie": "test_session=valid"},
        trust_env=False,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "subject": "verified-sub",
        "username": "verified-name",
        "authorization": "Bearer verified-token",
    }


def test_public_catalog_is_anonymous_and_strips_identity(proxy_url):
    response = httpx.get(
        proxy_url + "/api/v1/assistants/public", headers=FORGED_HEADERS, trust_env=False
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"subject": None, "username": None, "authorization": None}


def test_public_catalog_exception_does_not_cover_other_routes(proxy_url):
    response = httpx.get(
        proxy_url + "/api/v1/assistants/public/other",
        headers=FORGED_HEADERS,
        trust_env=False,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_auth_subrequest_cannot_be_called_directly(proxy_url):
    response = httpx.get(
        proxy_url + "/oauth2/auth", headers=FORGED_HEADERS, trust_env=False
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_public_catalog_does_not_allow_writes(proxy_url):
    response = httpx.post(
        proxy_url + "/api/v1/assistants/public", headers=FORGED_HEADERS, trust_env=False
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_unknown_host_is_not_forwarded(proxy_url):
    response = httpx.get(
        proxy_url + "/users/me", headers={"Host": "untrusted.example"}, trust_env=False
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_backend_redirects_keep_the_public_host(proxy_url):
    response = httpx.get(
        proxy_url + "/redirect",
        headers={"Host": "localhost", "Cookie": "test_session=valid"},
        trust_env=False,
    )
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["Location"] == "http://localhost/redirect/"


def test_compose_does_not_publish_auth_or_application_ports():
    config = yaml.safe_load((ROOT / "docker-compose.yaml").read_text())
    for service in (
        "app",
        "oauth2-proxy",
        "zitadel-api",
        "zitadel-login",
        "zitadel-db",
    ):
        assert not config["services"][service].get("ports")
