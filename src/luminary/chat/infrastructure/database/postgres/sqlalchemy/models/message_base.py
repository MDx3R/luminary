from __future__ import annotations

from datetime import datetime
from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from luminary.chat.domain.enums import Author, MessageStatus
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.attachment_base import (
    AttachmentBase,
)


class MessageBase(Base):
    __tablename__ = "messages"

    message_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)
    chat_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("chats.chat_id"), nullable=False
    )
    role: Mapped[Author] = mapped_column(Enum(Author), nullable=False)
    status: Mapped[MessageStatus] = mapped_column(Enum(MessageStatus), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    model_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    edited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    attachments: Mapped[list[AttachmentBase]] = relationship(
        "AttachmentBase", lazy="noload"
    )
