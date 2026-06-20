"""
ai/conversation.py - In-memory conversation history per email address
"""

from .maya import MAYA_SYSTEM_PROMPT

# Store conversation history per prospect email
# Format: {email: [{"role": "user/assistant/system", "content": "..."}]}
_conversations: dict = {}


def get_or_create_thread(email: str) -> list:
      """Get or initialise the conversation thread for a given email."""
      if email not in _conversations:
                _conversations[email] = [
                              {"role": "system", "content": MAYA_SYSTEM_PROMPT}
                ]
            return _conversations[email]


def add_message(email: str, role: str, content: str):
      """Append a message to the conversation thread."""
    thread = get_or_create_thread(email)
    thread.append({"role": role, "content": content})


def get_messages_for_api(email: str) -> list:
      """Return the full message list ready for the OpenAI API."""
    return get_or_create_thread(email)


def clear_thread(email: str):
      """Remove a conversation thread (e.g. after deal closed or error)."""
    _conversations.pop(email, None)
