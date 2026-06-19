"""
email/sender.py - Send emails from maya@makeyourlabel.com via Microsoft Graph API
"""

import logging
from config import settings
from .graph_client import graph_post

logger = logging.getLogger(__name__)


def send_email(
      to_email: str,
      to_name: str,
      subject: str,
      body_html: str,
      reply_to_message_id: str = None,
) -> bool:
      """
          Send an email from maya@makeyourlabel.com.
              Optionally pass reply_to_message_id to thread it as a reply.
                  Returns True on success.
                      """
      message = {
          "subject": subject,
          "body": {"contentType": "HTML", "content": body_html},
          "toRecipients": [
              {"emailAddress": {"address": to_email, "name": to_name}}
          ],
          "from": {
              "emailAddress": {
                  "address": settings.maya_email,
                  "name": "Maya | MakeYourLabel",
              }
          },
      }

    if reply_to_message_id:
              message["internetMessageHeaders"] = [
                            {"name": "In-Reply-To", "value": f"<{reply_to_message_id}>"},
                            {"name": "References", "value": f"<{reply_to_message_id}>"},
              ]

    try:
              graph_post(
                            f"users/{settings.maya_email}/sendMail",
                            {"message": message, "saveToSentItems": True}
              )
              logger.info(f"Email sent to {to_email} | Subject: {subject}")
              return True
except Exception as e:
          logger.error(f"Failed to send email to {to_email}: {e}")
          return False


def build_reply_subject(original_subject: str) -> str:
      """Prepend Re: to subject if not already there."""
      if original_subject.lower().startswith("re:"):
                return original_subject
            return f"Re: {original_subject}"
