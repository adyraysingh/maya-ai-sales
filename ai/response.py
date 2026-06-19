""
ai/response.py - Generate Maya's reply using GPT-4 via OpenAI API
"""

import logging
from openai import OpenAI
from config import settings
from .conversation import get_messages_for_api, add_message

logger = logging.getLogger(__name__)

# Lazy-init client
_client: OpenAI = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def generate_maya_response(
    prospect_email: str,
    prospect_message: str,
    lead_context: str = "",
) -> str:
    """
    Add the prospect's message to history and call GPT-4 to generate Maya's reply.
    Returns Maya's response text (plain text, ready to send as email).
    """
    # Add the prospect's incoming message to the conversation
    add_message(prospect_email, "user", prospect_message)

    # Get the full conversation history including the system prompt
    messages = get_messages_for_api(prospect_email)

    # If we have fresh lead context, inject it as a temporary system note
    if lead_context:
        enriched_messages = list(messages)
        enriched_messages.insert(1, {
            "role": "system",
            "content": f"[Lead context for your reference - do not mention this data explicitly]\n{lead_context}"
        })
    else:
        enriched_messages = messages

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=enriched_messages,
            temperature=0.85,
            max_tokens=600,
        )

        reply = response.choices[0].message.content.strip()
        logger.info(f"GPT-4 response generated for {prospect_email} ({len(reply)} chars)")

        # Add Maya's response to the conversation history
        add_message(prospect_email, "assistant", reply)

        return reply

    except Exception as e:
        logger.error(f"OpenAI API error for {prospect_email}: {e}")
        raise


def wrap_reply_in_html(text: str) -> str:
    """
    Convert plain text email reply to simple HTML.
    Preserves paragraph breaks and keeps the tone natural.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    html_parts = ["".join(f"<p>{line}</p>" for line in p.split("\n") if line) for p in paragraphs]
    return (
        '<div style="font-family:Arial,sans-serif;font-size:14px;line-height:1.6;color:#333;">'
        + "".join(html_parts)
        + "</div>"
    )
