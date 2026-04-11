from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import Boolean, ColumnElement, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from luminary.assistant.domain.enums import AssistantType


class AssistantBase(Base):
    __tablename__ = "assistants"

    assistant_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    type: Mapped[AssistantType] = mapped_column(Enum(AssistantType), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    @hybrid_property
    def is_active(self) -> bool:
        return not self.is_deleted

    @is_active.inplace.expression
    @classmethod
    def _is_active(cls) -> ColumnElement[bool]:
        return cls.is_deleted.is_not(True)
