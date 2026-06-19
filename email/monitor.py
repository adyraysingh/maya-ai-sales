"""
email/monitor.py - Poll maya@makeyourlabel.com inbox for new replies from prospects
Uses Microsoft Graph delta query to detect only new unread messages.
"""

import logging
import re
from typing import Optional
from config import settings
from .graph_client import graph_get, graph_patch

logger = logging.getLogger(__name__)

_delta_token: Optional[str] = None


def get_unread_messages() -> list:
      """Fetch unread messages from Maya inbox. Returns list of message dicts."""
      global _delta_token
      user_id = settings.maya_email

    select_fields = (
              "id,subject,from,toRecipients,receivedDateTime,"
              "body,conversationId,internetMessageId"
    )

    if _delta_token:
              endpoint = f"users/{user_id}/mailFolders/Inbox/messages/delta"
              params = {"$deltaToken": _delta_token}
else:
          endpoint = f"users/{user_id}/mailFolders/Inbox/messages/delta"
          params = {"$filter": "isRead eq false", "$select": select_fields, "$top": "20"}

    try:
              data = graph_get(endpoint, params=params)
              messages = data.get("value", [])

        delta_link = data.get("@odata.deltaLink", "")
        if delta_link and "$deltaToken=" in delta_link:
                      _delta_token = delta_link.split("$deltaToken=")[-1]

        incoming = []
        for msg in messages:
                      sender_addr = msg.get("from", {}).get("emailAddress", {}).get("address", "")
                      if sender_addr.lower() != settings.maya_email.lower():
                                        incoming.append(msg)
                                        _mark_as_read(user_id, msg["id"])

                  logger.info(f"Found {len(incoming)} new prospect messages.")
        return incoming

except Exception as e:
        logger.error(f"Error polling inbox: {e}")
        return []


def _mark_as_read(user_id: str, message_id: str) -> None:
      try:
                graph_patch(f"users/{user_id}/messages/{message_id}", {"isRead": True})
except Exception as e:
        logger.warning(f"Could not mark message {message_id} as read: {e}")


def extract_message_body(message: dict) -> str:
      """Extract clean plain text from Graph message body."""
      body = message.get("body", {})
      content = body.get("content", "")
      if body.get("contentType", "").lower() == "html":
                content = re.sub(r"<[^>]+>", " ", content)
                content = re.sub(r"&nbsp;", " ", content)
                content = re.sub(r"\s+", " ", content).strip()
            return content


def get_sender_email(message: dict) -> str:
      return message.get("from", {}).get("emailAddress", {}).get("address", "")


def get_sender_name(message: dict) -> str:
      return message.get("from", {}).get("emailAddress", {}).get("name", "")


def get_message_id(message: dict) -> str:
      return message.get("internetMessageId", message.get("id", ""))
