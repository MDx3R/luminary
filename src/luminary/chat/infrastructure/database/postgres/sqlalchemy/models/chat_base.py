from __future__ import annotations

from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import Boolean, ColumnElement, ForeignKey, Integer, String, and_
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from luminary.assistant.infrastructure.database.postgres.sqlalchemy.models.assistant_base import (
    AssistantBase,
)
from luminary.source.infrastructure.database.postgres.sqlalchemy.models.source_base import (
    SourceBase,
)


class ChatSourceAssociation(Base):
    __tablename__ = "chat_sources"

    chat_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("chats.chat_id"), primary_key=True
    )
    source_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)


class ChatBase(Base):
    __tablename__ = "chats"

    chat_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    folder_id: Mapped[UUID | None] = mapped_column(PGUUID, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    assistant_id: Mapped[UUID | None] = mapped_column(PGUUID, nullable=True)
    model_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    max_context_messages: Mapped[int] = mapped_column(Integer, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    source_associations: Mapped[list[ChatSourceAssociation]] = relationship(
        "ChatSourceAssociation", lazy="noload"
    )
    sources: Mapped[list[SourceBase]] = relationship(
        "SourceBase",
        secondary="chat_sources",
        primaryjoin=and_(chat_id == ChatSourceAssociation.chat_id),
        secondaryjoin=and_(
            SourceBase.source_id == ChatSourceAssociation.source_id,
            SourceBase.is_active,
        ),
        lazy="noload",
        viewonly=True,
    )
    assistant: Mapped[AssistantBase | None] = relationship(
        "AssistantBase",
        primaryjoin=and_(foreign(assistant_id) == AssistantBase.assistant_id),
        lazy="noload",
        viewonly=True,
    )

    @hybrid_property
    def is_active(self) -> bool:
        return not self.is_deleted

    @is_active.inplace.expression
    @classmethod
    def _is_active(cls) -> ColumnElement[bool]:
        return cls.is_deleted.is_not(True)
