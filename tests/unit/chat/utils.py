from datetime import datetime, timezone
from uuid import uuid4
from src.luminary.chat.domain.entity.chat import Chat, ChatInfo, ChatSettings
from src.luminary.chat.domain.entity.message import Message
from src.luminary.chat.domain.enums import Author, MessageStatus

def make_chat(
    chat_id=None,
    user_id=None,
    name="Test Chat",
    system_prompt="Test prompt",
    max_context_messages=10,
    model_id=None,
    folder_id=None,  
    created_at=None  
):
    chat_id = chat_id or uuid4()
    user_id = user_id or uuid4()
    model_id = model_id or uuid4()
    
    if created_at is None:
        created_at = datetime.now()
    
    chat_info = ChatInfo(name=name)
    chat_settings = ChatSettings(
        model_id=model_id,
        system_prompt=system_prompt,
        max_context_messages=max_context_messages
    )

    return Chat(
        chat_id=chat_id,
        user_id=user_id,
        folder_id=folder_id,  
        created_at=created_at,  
        info=chat_info,
        settings=chat_settings
    )

def make_message(
    message_id=None,
    chat_id=None,
    model_id=None,
    content="Test message",  
    role=Author.USER,
    status=MessageStatus.PENDING,
    tokens=None,
    created_at=None,
    edited_at=None
):
    message_id = message_id or uuid4()
    chat_id = chat_id or uuid4()
    model_id = model_id or uuid4()
    
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    elif created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    
    if edited_at is None:
        edited_at = created_at
    elif edited_at.tzinfo is None:
        edited_at = edited_at.replace(tzinfo=timezone.utc)
    
    return Message(
        message_id=message_id,
        chat_id=chat_id,
        model_id=model_id,
        content=content,
        role=role,
        status=status,
        tokens=tokens,
        created_at=created_at,
        edited_at=edited_at
    )