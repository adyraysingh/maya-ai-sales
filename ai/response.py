"""
ai/response.py - Generate Maya's reply using GPT-4
"""

import logging
from openai import OpenAI
from config import settings
from .conversation import get_messages_for_api, add_message

logger = logging.getLogger(__name__)
_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def generate_maya_response(
    prospect_email: str,
    prospect_message: str,
    lead_context: str = "",
) -> str:
    add_message(prospect_email, "user", prospect_message)
    messages = get_messages_for_api(prospect_email)

    if lead_context:
        enriched = list(messages)
        enriched.insert(1, {
            "role": "system",
            "content": f"[Lead context - do not mention explicitly]
{lead_context}"
        })
    else:
        enriched = messages

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=enriched,
            temperature=0.85,
            max_tokens=600,
        )
        reply = response.choices[0].message.content.strip()
        add_message(prospect_email, "assistant", reply)
        logger.info(f"GPT-4 reply generated for {prospect_email}")
        return reply
    except Exception as e:
        logger.error(f"OpenAI API error for {prospect_email}: {e}")
        raise


def wrap_reply_in_html(text: str) -> str:
    paragraphs = [p.strip() for p in text.split("

") if p.strip()]
    html_parts = [
        "".join(f"<p>{line}</p>" for line in p.split("
") if line)
        for p in paragraphs
    ]
    return (
        '<div style="font-family:Arial,sans-serif;font-size:14px;line-height:1.6;color:#333;">'
        + "".join(html_parts)
        + "</div>"
    )
