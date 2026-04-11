from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime

from luminary.chat.domain.entity.attachment import Attachment
from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.enums import Author, MessageStatus
from luminary.chat.domain.events.events import (
    MessageCancelledEvent,
    MessageCompletedEvent,
    MessageFailedEvent,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.message_id import MessageId
from luminary.model.domain.entity.model import ModelId
from luminary.source.domain.entity.source import SourceId


class TestAttachment:
    def test_create_success(self):
        att = Attachment(
            name="file.txt", content_id=uuid4(), source_id=SourceId(uuid4())
        )
        assert att.name == "file.txt"

    @pytest.mark.parametrize("name", ["", "   "])
    def test_invalid_name_raises(self, name: Literal[""] | Literal["   "]):
        with pytest.raises(InvariantViolationError):
            Attachment(name=name, content_id=uuid4(), source_id=SourceId(uuid4()))


class TestMessage:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.message_id = MessageId(uuid4())
        self.chat_id = ChatId(uuid4())
        self.model_id = ModelId(uuid4())
        self.content = "Hello, world!"
        self.created_at = DateTime(datetime.now(UTC))

        self.message = Message(
            id=self.message_id,
            chat_id=self.chat_id,
            model_id=self.model_id,
            content=self.content,
            role=Author.USER,
            status=MessageStatus.COMPLETED,
            created_at=self.created_at,
            edited_at=self.created_at,
        )

    def test_attachments_property_empty(self):
        assert self.message.attachments == []

    def test_add_attachment_success(self):
        att = Attachment(
            name="file.txt", content_id=uuid4(), source_id=SourceId(uuid4())
        )
        self.message.add_attachment(att)
        assert att in self.message.attachments

    def test_add_attachment_non_user_raises(self):
        self.message.role = Author.SYSTEM
        att = Attachment(
            name="file.txt", content_id=uuid4(), source_id=SourceId(uuid4())
        )
        with pytest.raises(InvariantViolationError):
            self.message.add_attachment(att)

    def test_create_message_success(self):
        message = Message.create(
            id=self.message_id,
            chat_id=self.chat_id,
            model_id=self.model_id,
            content=self.content,
            role=Author.USER,
            status=MessageStatus.COMPLETED,
            created_at=self.created_at,
        )
        assert message == self.message

    def test_message_naive_datetime_raises_error(self):
        with pytest.raises(InvariantViolationError):
            Message(
                id=self.message_id,
                chat_id=self.chat_id,
                model_id=self.model_id,
                content="Test message",
                role=Author.USER,
                status=MessageStatus.PENDING,
                created_at=DateTime(datetime.now()),
                edited_at=DateTime(datetime.now()),
            )

    def test_add_chunk_success(self):
        self.message.content = "Hello"
        self.message.add_chunk(" world")
        assert self.message.content == "Hello world"

    def test_start_processing_changes_status(self):
        self.message.start_processing()
        assert self.message.status == MessageStatus.PROCESSING

    def test_start_streaming_changes_status(self):
        self.message.start_streaming()
        assert self.message.status == MessageStatus.STREAMING

    def test_cancel_changes_status(self):
        self.message.status = MessageStatus.PROCESSING
        self.message.cancel()
        assert self.message.status == MessageStatus.CANCELLED
        assert len(self.message.events) == 1
        assert isinstance(self.message.events[0], MessageCancelledEvent)

    def test_fail_changes_status(self):
        self.message.status = MessageStatus.PROCESSING
        self.message.fail()
        assert self.message.status == MessageStatus.FAILED
        assert len(self.message.events) == 1
        assert isinstance(self.message.events[0], MessageFailedEvent)

    def test_complete_changes_status_and_sets_tokens(self):
        self.message.status = MessageStatus.STREAMING
        self.message.tokens = None
        tokens = 150
        self.message.complete(tokens)
        assert self.message.status == MessageStatus.COMPLETED
        assert self.message.tokens == tokens
        assert len(self.message.events) == 1
        assert isinstance(self.message.events[0], MessageCompletedEvent)
        assert self.message.events[0].tokens == tokens
