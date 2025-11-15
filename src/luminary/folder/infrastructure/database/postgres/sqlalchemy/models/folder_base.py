from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class FolderSourceBase(Base):
    __tablename__ = "folder_sources"

    folder_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("folders.folder_id"), primary_key=True
    )

    # TODO: Add FK
    source_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)


class FolderChatBase(Base):
    __tablename__ = "folder_sources"

    folder_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("folders.folder_id"), primary_key=True
    )

    # TODO: Add FK
    chat_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)


class FolderBase(Base):
    __tablename__ = "folders"

    folder_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    # TODO: Add FK
    user_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    assistant_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)

    # TODO: Add relations
    sources: Mapped[list[FolderSourceBase]] = relationship(
        "FolderSourceBase", cascade="all, delete-orphan", lazy="noload"
    )
    chats: Mapped[list[FolderChatBase]] = relationship(
        "FolderChatBase", cascade="all, delete-orphan", lazy="noload"
    )
