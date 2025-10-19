from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column


class ChatBase(Base):
    __tablename__ = "chats"

    chat_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    system_prompt: Mapped[str | None] = mapped_column(String, nullable=True)
    max_context_messages: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # TODO: Add FK
    user_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    folder_id: Mapped[UUID | None] = mapped_column(PGUUID, nullable=True)
    model_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)

    # TODO: Add relations
