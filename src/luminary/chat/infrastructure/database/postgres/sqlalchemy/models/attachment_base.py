from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column


class AttachmentBase(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("messages.message_id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    content_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    source_id: Mapped[UUID | None] = mapped_column(PGUUID, nullable=True)
