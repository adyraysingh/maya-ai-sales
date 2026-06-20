"""
ai/conversation.py - Conversation history manager
"""
from .maya import MAYA_SYSTEM_PROMPT

_conversations: dict = {}


def get_or_create_thread(email: str) -> list:
    if email not in _conversations:
        _conversations[email] = [{"role": "system", "content": MAYA_SYSTEM_PROMPT}]
    return _conversations[email]


def add_message(email: str, role: str, content: str):
    thread = get_or_create_thread(email)
    thread.append({"role": role, "content": content})


def get_messages_for_api(email: str) -> list:
    return get_or_create_thread(email)


def clear_thread(email: str):
    _conversations.pop(email, None)
