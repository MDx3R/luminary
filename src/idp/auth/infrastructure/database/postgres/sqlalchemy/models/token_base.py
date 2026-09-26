from datetime import datetime
from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column


class TokenBase(Base):
    __tablename__ = "tokens"

    token_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)
    identity_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)  # NOTE: No FK
    value: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
