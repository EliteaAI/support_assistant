from datetime import datetime
from typing import Any

ASSISTANT_PARTICIPANT_TYPES = {'application', 'llm', 'dummy'}


def to_fe_timestamp(value: Any) -> int:
    """Convert various timestamp formats to FE format (Unix ms)."""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        if value < 4102444800:
            return int(value * 1000)
        return int(value)
    if isinstance(value, datetime):
        return int(value.timestamp() * 1000)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return int(dt.timestamp() * 1000)
        except ValueError:
            return 0
    return 0


def _participant_type_to_role(participant_type: str) -> str:
    """Map BE participant type to FE role ('user' | 'assistant')."""
    if participant_type in ASSISTANT_PARTICIPANT_TYPES:
        return 'assistant'
    return 'user'


def to_fe_conversation(conv: dict) -> dict:
    """Transform BE conversation to FE TConversation format."""
    return {
        'id': str(conv.get('uuid', conv.get('id', ''))),
        'title': conv.get('name', 'New conversation'),
        'createdAt': to_fe_timestamp(
            conv.get('created_at_ts') or conv.get('created_at')
        ),
    }


def to_fe_message(msg: dict) -> dict:
    """Transform BE message group to FE TMessage format."""
    sent_to = msg.get('sent_to')
    role = 'user' if sent_to is not None else 'assistant'

    content = ''
    message_items = msg.get('message_items', [])
    for item in message_items:
        item_type = item.get('item_type') or item.get('type')
        if item_type in ('text_message', 'text'):
            item_details = item.get('item_details', {})
            if item_details:
                content = item_details.get('content', '')
            else:
                content = item.get('content', '')
            break

    return {
        'id': str(msg.get('uuid', msg.get('id', ''))),
        'role': role,
        'content': content,
        'timestamp': to_fe_timestamp(
            msg.get('created_at_ts') or msg.get('created_at')
        ),
    }


def to_fe_config(config: dict, enabled: bool) -> dict:
    """Transform plugin config to FE widget props."""
    if not enabled:
        return {'enabled': False}

    return {
        'enabled': True,
        'title': config.get('assistant_name', 'ELITEA Support'),
        'welcomeMessage': config.get('welcome_message', ''),
        'placeholder': config.get('placeholder', 'Type a message...'),
    }
