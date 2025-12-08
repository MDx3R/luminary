from datetime import datetime
from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from luminary.source.domain.enums import FetchStatus, SourceType


class SourceBase(Base):
    __tablename__ = "sources"

    source_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)

    type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    fetch_status: Mapped[FetchStatus] = mapped_column(Enum(FetchStatus), nullable=False)

    # TODO: Add FK
    owner_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    content_id: Mapped[UUID | None] = mapped_column(PGUUID, nullable=True)

    __mapper_args__ = {"polymorphic_on": "type"}  # noqa: RUF012


class FileSourceBase(SourceBase):
    __tablename__ = "file_sources"

    source_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("sources.source_id"), primary_key=True
    )

    # TODO: Add FK
    file_id: Mapped[UUID] = mapped_column(PGUUID)

    __mapper_args__ = {"polymorphic_identity": SourceType.FILE}  # noqa: RUF012


class LinkSourceBase(SourceBase):
    __tablename__ = "link_sources"

    source_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("sources.source_id"), primary_key=True
    )
    url: Mapped[str] = mapped_column(String, nullable=False)

    __mapper_args__ = {"polymorphic_identity": SourceType.LINK}  # noqa: RUF012


class PageSourceBase(SourceBase):
    __tablename__ = "page_sources"

    source_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("sources.source_id"), primary_key=True
    )
    editable: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __mapper_args__ = {"polymorphic_identity": SourceType.PAGE}  # noqa: RUF012
