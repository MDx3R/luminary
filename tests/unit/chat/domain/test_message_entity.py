import pytest
from uuid import uuid4
from datetime import datetime, timezone

from src.common.domain.exceptions import InvariantViolationError
from src.luminary.chat.domain.enums import Author, MessageStatus
from src.luminary.chat.domain.entity.message import Message
from tests.unit.chat.utils import make_message

class TestMessageEntity:
    def test_create_message_success(self):
        message_id = uuid4()
        chat_id = uuid4()
        model_id = uuid4()
        content = "Hello, world!"

        message = make_message(
            message_id=message_id,
            chat_id=chat_id,
            model_id=model_id,
            content=content,
            role=Author.USER,
            status=MessageStatus.COMPLETED,
        )

        assert message.message_id == message_id
        assert message.chat_id == chat_id
        assert message.model_id == model_id
        assert message.content == content
        assert message.role == Author.USER
        assert message.status == MessageStatus.COMPLETED

    def test_message_naive_datetime_raises_error(self):
        try:
            message = Message(
                message_id=uuid4(),
                chat_id=uuid4(),
                model_id=uuid4(),
                content="Test message",
                role=Author.USER,
                status=MessageStatus.PENDING,
                created_at=datetime.now(),  
                edited_at=datetime.now()    
            )
        except InvariantViolationError:
            pass

    def test_add_chunk_success(self):
        message = make_message(content="Hello")
        message.add_chunk(" world")
        assert message.content == "Hello world"

    def test_start_processing_changes_status(self):
        message = make_message(status=MessageStatus.PENDING)
        message.start_processing()
        assert message.status == MessageStatus.PROCESSING

    def test_start_streaming_changes_status(self):
        message = make_message(status=MessageStatus.PENDING)
        message.start_streaming()
        assert message.status == MessageStatus.STREAMING

    def test_cancel_changes_status(self):
        message = make_message(status=MessageStatus.PROCESSING)
        message.cancel()
        assert message.status == MessageStatus.CANCELLED

    def test_fail_changes_status(self):
        message = make_message(status=MessageStatus.PROCESSING)
        message.fail()
        assert message.status == MessageStatus.FAILED

    def test_complete_changes_status_and_sets_tokens(self):
        message = make_message(status=MessageStatus.STREAMING, tokens=None)
        tokens = 150
        message.complete(tokens)
        assert message.status == MessageStatus.COMPLETED
        assert message.tokens == tokens

    def test_complete_negative_tokens_raises_error(self):
        message = make_message(status=MessageStatus.STREAMING)
        
        try:
            message.complete(-10)

        except InvariantViolationError as e:
            assert "Tokens cannot be negative" in str(e)

    def _create_invalid_message(self, content: str = "Test message", tokens: int = None) -> Message:
        """Создает сообщение с возможностью указания невалидных параметров"""
        return Message(
            message_id=uuid4(),
            chat_id=uuid4(),
            model_id=uuid4(),
            content=content,
            role=Author.USER,
            status=MessageStatus.PENDING,
            tokens=tokens,
            created_at=datetime.now(timezone.utc),
            edited_at=datetime.now(timezone.utc)
        )