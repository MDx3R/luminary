import secrets

from common.domain.interfaces.token_generator import ITokenGenerator


class SecretsTokenGenerator(ITokenGenerator):
    def hex(self, length: int) -> str:
        self.validate_length(length)
        return secrets.token_hex(length)[:length]

    def numeric(self, length: int) -> str:
        self.validate_length(length)
        if not length:
            return ""

        return str(secrets.randbelow(10**length)).zfill(length)

    def urlsafe(self, length: int) -> str:
        self.validate_length(length)
        return secrets.token_urlsafe(length)

    def secure(self, length: int = 64) -> str:
        return self.urlsafe(length)

    def validate_length(self, length: int) -> None:
        if length < 0:
            raise ValueError(f"Token length must be non-negative, got {length}")
