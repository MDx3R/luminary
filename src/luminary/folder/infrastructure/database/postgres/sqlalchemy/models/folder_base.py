from __future__ import annotations

from datetime import datetime
from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import Boolean, ColumnElement, DateTime, ForeignKey, String, Text, and_
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from luminary.assistant.infrastructure.database.postgres.sqlalchemy.models.assistant_base import (
    AssistantBase,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
)
from luminary.source.infrastructure.database.postgres.sqlalchemy.models.source_base import (
    SourceBase,
)


class FolderChatAssociation(Base):
    __tablename__ = "folder_chats"

    folder_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("folders.folder_id"), primary_key=True
    )
    chat_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)


class FolderSourceAssociation(Base):
    __tablename__ = "folder_sources"

    folder_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("folders.folder_id"), primary_key=True
    )
    source_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)


class FolderBase(Base):
    __tablename__ = "folders"

    folder_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    assistant_id: Mapped[UUID | None] = mapped_column(PGUUID, nullable=True)
    editor_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    editor_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    chat_associations: Mapped[list[FolderChatAssociation]] = relationship(
        "FolderChatAssociation", lazy="noload"
    )
    source_associations: Mapped[list[FolderSourceAssociation]] = relationship(
        "FolderSourceAssociation", lazy="noload"
    )
    assistant: Mapped[AssistantBase | None] = relationship(
        "AssistantBase",
        primaryjoin=and_(foreign(assistant_id) == AssistantBase.assistant_id),
        lazy="noload",
        viewonly=True,
    )
    chats: Mapped[list[ChatBase]] = relationship(
        "ChatBase",
        secondary="folder_chats",
        primaryjoin=and_(folder_id == FolderChatAssociation.folder_id),
        secondaryjoin=and_(
            ChatBase.chat_id == FolderChatAssociation.chat_id,
            ChatBase.is_active,
        ),
        lazy="noload",
        viewonly=True,
    )
    sources: Mapped[list[SourceBase]] = relationship(
        "SourceBase",
        secondary="folder_sources",
        primaryjoin=and_(folder_id == FolderSourceAssociation.folder_id),
        secondaryjoin=and_(
            SourceBase.source_id == FolderSourceAssociation.source_id,
            SourceBase.is_active,
        ),
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
