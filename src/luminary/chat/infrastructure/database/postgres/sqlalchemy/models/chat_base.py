from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import ForeignKey, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ChatSourceBase(Base):
    __tablename__ = "chat_sources"

    chat_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("chats.chat_id"), primary_key=True
    )

    # TODO: Add FK
    source_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)


class ChatBase(Base):
    __tablename__ = "chats"

    chat_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    system_prompt: Mapped[str] = mapped_column(String, nullable=False)
    max_context_messages: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # TODO: Add FK
    user_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    folder_id: Mapped[UUID | None] = mapped_column(PGUUID, nullable=True)
    model_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)

    # TODO: Add relations

    sources: Mapped[list[ChatSourceBase]] = relationship(
        "ChatSourceBase", cascade="all, delete-orphan", lazy="noload"
    )
