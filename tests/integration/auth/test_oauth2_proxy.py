"""Exercise the real proxy's code exchange and session claims against a test issuer."""

import base64
import json
import secrets
import time
from contextlib import ExitStack
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
import yaml
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from fastapi import status
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs
from tests.integration.auth.test_proxy import FORGED_HEADERS
from tests.integration.auth.test_zitadel_stack import proxy_image, wait_for_proxy


ROOT = Path(__file__).resolve().parents[3]
ISSUER = "http://oidc:8080"


def encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def public_jwk(key: rsa.RSAPrivateKey) -> str:
    numbers = key.public_key().public_numbers()
    return json.dumps(
        {
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "kid": "test",
            "n": encode(numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")),
            "e": encode(numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")),
        }
    )


def signed_token(
    key: rsa.RSAPrivateKey,
    session_nonce: str,
    verified: bool,
    client_id: str,
    **overrides: str | int | bool,
) -> str:
    header = encode(json.dumps({"alg": "RS256", "kid": "test"}).encode())
    claims = encode(
        json.dumps(
            {
                "iss": ISSUER,
                "aud": client_id,
                "sub": "verified-sub",
                "exp": int(time.time()) + 3600,
                "iat": int(time.time()),
                "nonce": session_nonce,
                "email": "verified@example.com",
                "email_verified": verified,
                "preferred_username": "verified-name",
                "name": "Verified Name",
            }
            | overrides
        ).encode()
    )
    message = f"{header}.{claims}".encode()
    signature = key.sign(message, padding.PKCS1v15(), hashes.SHA256())
    return f"{header}.{claims}.{encode(signature)}"


def nginx_container(network: Network) -> DockerContainer:
    return (
        DockerContainer("nginx:1.28-alpine")
        .with_network(network)
        .with_exposed_ports(80)
        .with_env("APP_DOMAIN", "localhost")
        .with_env("APP_ORIGIN", "http://localhost")
        .with_env("ZITADEL_DOMAIN", "zitadel.localhost")
        .with_env("NGINX_ENVSUBST_OUTPUT_DIR", "/etc/nginx")
        .with_env("NGINX_ENVSUBST_FILTER", "^(APP_DOMAIN|APP_ORIGIN|ZITADEL_DOMAIN)$")
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


@pytest.fixture(
    scope="module",
    params=["test-client", "123456789012345678"],
    ids=["text-client-id", "numeric-client-id"],
)
def client_id(request):
    return request.param


@pytest.fixture(scope="module")
def oidc_stack(client_id):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with Network() as network, ExitStack() as stack:
        issuer = (
            DockerContainer("python:3.12-alpine")
            .with_network(network)
            .with_network_aliases("oidc")
            .with_exposed_ports(8080)
            .with_env("TEST_JWK", public_jwk(key))
            .with_command(
                ["python", "-c", Path(__file__).with_name("oidc_stub.py").read_text()]
            )
        )
        stack.enter_context(issuer)
        wait_for_logs(issuer, "issuer ready")
        backend = (
            DockerContainer("python:3.12-alpine")
            .with_network(network)
            .with_network_aliases("app")
            .with_command(
                ["python", "-c", Path(__file__).with_name("proxy_stub.py").read_text()]
            )
        )
        stack.enter_context(backend)
        wait_for_logs(backend, "stub ready")
        service = yaml.safe_load((ROOT / "docker-compose.yaml").read_text())[
            "services"
        ]["oauth2-proxy"]
        image = proxy_image(
            issuer.get_wrapped_container().client, stack, service["image"]
        )
        proxy = (
            DockerContainer(image)
            .with_network(network)
            .with_network_aliases("oauth2-proxy")
            .with_command(service["command"])
            .with_env("LUMINARY_OIDC_ISSUER_URL", ISSUER)
            .with_env("LUMINARY_OIDC_CLIENT_ID", client_id)
            .with_env("LUMINARY_OIDC_CLIENT_SECRET", secrets.token_urlsafe(32))
            .with_env("OAUTH2_PROXY_COOKIE_SECRET", secrets.token_urlsafe(32))
            .with_env("OAUTH2_PROXY_COOKIE_SECURE", "false")
            .with_env("OAUTH2_PROXY_REDIRECT_URL", "http://localhost/oauth2/callback")
        )
        stack.enter_context(proxy)
        wait_for_proxy(proxy)
        nginx = stack.enter_context(nginx_container(network))
        wait_for_logs(nginx, "start worker processes")
        yield (
            f"http://{nginx.get_container_host_ip()}:{nginx.get_exposed_port(80)}",
            f"http://{issuer.get_container_host_ip()}:{issuer.get_exposed_port(8080)}",
            key,
        )


def login(
    client: httpx.Client,
    issuer_url: str,
    key,
    verified: bool = True,
    **overrides: str | int | bool,
):
    start = client.get("/oauth2/start")
    assert start.status_code == status.HTTP_302_FOUND
    parameters = parse_qs(urlsplit(start.headers["Location"]).query)
    code = secrets.token_urlsafe(16)
    token = signed_token(
        key, parameters["nonce"][0], verified, parameters["client_id"][0], **overrides
    )
    response = httpx.post(
        issuer_url + "/test/token",
        json={"code": code, "id_token": token},
        trust_env=False,
    )
    response.raise_for_status()
    return client.get(
        "/oauth2/callback", params={"code": code, "state": parameters["state"][0]}
    )


def test_authorization_request_preserves_client_id(oidc_stack, client_id):
    base_url, _, _ = oidc_stack
    with httpx.Client(
        base_url=base_url, headers={"Host": "localhost"}, trust_env=False
    ) as client:
        response = client.get("/oauth2/start")
        assert response.status_code == status.HTTP_302_FOUND
        parameters = parse_qs(urlsplit(response.headers["Location"]).query)
        assert parameters["client_id"] == [client_id]


def test_verified_session_provides_profile_without_credentials(oidc_stack):
    base_url, issuer_url, key = oidc_stack
    with httpx.Client(
        base_url=base_url, headers=FORGED_HEADERS, trust_env=False
    ) as client:
        assert login(client, issuer_url, key).status_code == status.HTTP_302_FOUND
        response = client.get("/users/me")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "subject": "verified-sub",
            "username": "verified-name",
            "name": "Verified Name",
            "email": "verified@example.com",
            "authorization": None,
            "cookie": None,
            "proxy_authorization": None,
            "forwarded_token": None,
            "auth_request_token": None,
        }
        assert client.get("/oauth2/sign_out").status_code == status.HTTP_302_FOUND
        assert client.get("/users/me").status_code == status.HTTP_401_UNAUTHORIZED


def test_unverified_email_cannot_create_a_session(oidc_stack):
    base_url, issuer_url, key = oidc_stack
    with httpx.Client(
        base_url=base_url, headers={"Host": "localhost"}, trust_env=False
    ) as client:
        assert login(client, issuer_url, key, verified=False).is_error
        assert client.get("/users/me").status_code == status.HTTP_401_UNAUTHORIZED


def test_invalid_signature_cannot_create_a_session(oidc_stack):
    base_url, issuer_url, _ = oidc_stack
    wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with httpx.Client(
        base_url=base_url, headers={"Host": "localhost"}, trust_env=False
    ) as client:
        assert login(client, issuer_url, wrong_key).is_error
        assert client.get("/users/me").status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "claims",
    [
        {"nonce": "wrong-nonce"},
        {"exp": 1},
        {"iss": "https://untrusted.example"},
        {"aud": "another-client"},
    ],
)
def test_invalid_claims_cannot_create_a_session(oidc_stack, claims):
    base_url, issuer_url, key = oidc_stack
    with httpx.Client(
        base_url=base_url, headers={"Host": "localhost"}, trust_env=False
    ) as client:
        assert login(client, issuer_url, key, **claims).is_error
        assert client.get("/users/me").status_code == status.HTTP_401_UNAUTHORIZED


def test_tampered_session_cookie_is_rejected(oidc_stack):
    base_url, issuer_url, key = oidc_stack
    with httpx.Client(
        base_url=base_url, headers=FORGED_HEADERS, trust_env=False
    ) as client:
        assert login(client, issuer_url, key).status_code == status.HTTP_302_FOUND
        cookie = client.cookies.get("_oauth2_proxy")
        assert cookie
        client.cookies.clear()
        client.cookies.set(
            "_oauth2_proxy", cookie[:-1] + ("a" if cookie[-1] != "a" else "b")
        )
        assert client.get("/users/me").status_code == status.HTTP_401_UNAUTHORIZED
