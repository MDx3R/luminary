from common.domain.value_objects.datetime import DateTime
from idp.auth.domain.entity.token import Token, TokenTypeEnum
from idp.auth.infrastructure.database.postgres.sqlalchemy.models.token_base import (
    TokenBase,
)


class TokenMapper:
    @classmethod
    def to_domain(cls, base: TokenBase) -> Token:
        return Token(
            token_id=base.token_id,
            identity_id=base.identity_id,
            value=base.value,
            token_type=TokenTypeEnum.REFRESH,
            issued_at=DateTime(base.issued_at),
            expires_at=DateTime(base.expires_at),
            revoked=base.revoked,
        )

    @classmethod
    def to_persistence(cls, token: Token) -> TokenBase:
        return TokenBase(
            token_id=token.token_id,
            identity_id=token.identity_id,
            value=token.value,
            issued_at=token.issued_at.value,
            expires_at=token.expires_at.value,
            revoked=token.revoked,
        )
