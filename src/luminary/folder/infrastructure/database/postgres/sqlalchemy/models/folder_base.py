from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column


class FolderBase(Base):
    __tablename__ = "folders"

    folder_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    # TODO: Add FK
    user_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    model_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    assistant_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)

    # TODO: Add relations
