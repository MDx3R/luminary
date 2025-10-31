from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime

from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.enums import Author, MessageStatus


class TestMessageEntity:
    def test_create_message_success(self) -> None:
        message_id: UUID = uuid4()
        chat_id: UUID = uuid4()
        model_id: UUID = uuid4()
        content: str = "Hello, world!"
        created_at: DateTime = DateTime(datetime.now(UTC))

        message: Message = Message(
            message_id=message_id,
            chat_id=chat_id,
            model_id=model_id,
            content=content,
            role=Author.USER,
            status=MessageStatus.COMPLETED,
            created_at=created_at,
            edited_at=created_at,
        )

        assert message.message_id == message_id
        assert message.chat_id == chat_id
        assert message.model_id == model_id
        assert message.content == content
        assert message.role == Author.USER
        assert message.status == MessageStatus.COMPLETED

    def test_message_naive_datetime_raises_error(self) -> None:
        with pytest.raises(InvariantViolationError):
            Message(
                message_id=uuid4(),
                chat_id=uuid4(),
                model_id=uuid4(),
                content="Test message",
                role=Author.USER,
                status=MessageStatus.PENDING,
                created_at=DateTime(datetime.now()),
                edited_at=DateTime(datetime.now()),
            )

    def test_add_chunk_success(self) -> None:
        message: Message = Message(
            message_id=uuid4(),
            chat_id=uuid4(),
            model_id=uuid4(),
            content="Hello",
            role=Author.USER,
            status=MessageStatus.PENDING,
            created_at=DateTime(datetime.now(UTC)),
            edited_at=DateTime(datetime.now(UTC)),
        )

        message.add_chunk(" world")

        assert message.content == "Hello world"

    def test_start_processing_changes_status(self) -> None:
        message: Message = Message(
            message_id=uuid4(),
            chat_id=uuid4(),
            model_id=uuid4(),
            content="Test",
            role=Author.USER,
            status=MessageStatus.PENDING,
            created_at=DateTime(datetime.now(UTC)),
            edited_at=DateTime(datetime.now(UTC)),
        )

        message.start_processing()

        assert message.status == MessageStatus.PROCESSING

    def test_start_streaming_changes_status(self) -> None:
        message: Message = Message(
            message_id=uuid4(),
            chat_id=uuid4(),
            model_id=uuid4(),
            content="Test",
            role=Author.USER,
            status=MessageStatus.PENDING,
            created_at=DateTime(datetime.now(UTC)),
            edited_at=DateTime(datetime.now(UTC)),
        )

        message.start_streaming()

        assert message.status == MessageStatus.STREAMING

    def test_cancel_changes_status(self) -> None:
        message: Message = Message(
            message_id=uuid4(),
            chat_id=uuid4(),
            model_id=uuid4(),
            content="Test",
            role=Author.USER,
            status=MessageStatus.PROCESSING,
            created_at=DateTime(datetime.now(UTC)),
            edited_at=DateTime(datetime.now(UTC)),
        )

        message.cancel()

        assert message.status == MessageStatus.CANCELLED

    def test_fail_changes_status(self) -> None:
        message: Message = Message(
            message_id=uuid4(),
            chat_id=uuid4(),
            model_id=uuid4(),
            content="Test",
            role=Author.USER,
            status=MessageStatus.PROCESSING,
            created_at=DateTime(datetime.now(UTC)),
            edited_at=DateTime(datetime.now(UTC)),
        )

        message.fail()

        assert message.status == MessageStatus.FAILED

    def test_complete_changes_status_and_sets_tokens(self) -> None:
        message: Message = Message(
            message_id=uuid4(),
            chat_id=uuid4(),
            model_id=uuid4(),
            content="Test",
            role=Author.USER,
            status=MessageStatus.STREAMING,
            tokens=None,
            created_at=DateTime(datetime.now(UTC)),
            edited_at=DateTime(datetime.now(UTC)),
        )

        tokens: int = 150
        message.complete(tokens)

        assert message.status == MessageStatus.COMPLETED
        assert message.tokens == tokens
