from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column


class SourceBase(Base):
    __tablename__ = "sources"

    source_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)

    # TODO: Add FK
    user_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)

    # TODO: Add relations
