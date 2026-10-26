from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column


class UserBase(Base):
    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)
    # NULL is reserved for legacy users awaiting an explicit administrator link.
    zitadel_sub: Mapped[str | None] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String)
