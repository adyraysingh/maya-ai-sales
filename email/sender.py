""
email/sender.py - Send emails from maya@makeyourlabel.com via Gmail SMTP
"""

import importlib
import smtplib
import logging
import re
from config import settings

# Load stdlib email submodules via importlib to avoid conflict with email/ folder
_MIMEMultipart = importlib.import_module("email.mime.multipart").MIMEMultipart
_MIMEText = importlib.import_module("email.mime.text").MIMEText
_formataddr = importlib.import_module("email.utils").formataddr

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
        to_name: str,
            subject: str,
                body_html: str,
                    reply_to_message_id: str = None,
                    ) -> bool:
                        """
    Send an email from maya@makeyourlabel.com via Gmail SMTP.
    Optionally pass reply_to_message_id to thread it as a reply.
    Returns True on success.
    """
          try:
        msg = _MIMEMultipart("alternative")
        msg["From"] = _formataddr(("Maya | MakeYourLabel", settings.MAYA_EMAIL))
        msg["To"] = _formataddr((to_name, to_email))
        msg["Subject"] = subject

        if reply_to_message_id:
                      msg["In-Reply-To"] = reply_to_message_id
                      msg["References"] = reply_to_message_id

        body_text = body_html.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
        body_text = re.sub(r"<[^>]+>", "", body_text).strip()

        msg.attach(_MIMEText(body_text, "plain"))
        msg.attach(_MIMEText(body_html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                      server.login(settings.MAYA_EMAIL, settings.GMAIL_APP_PASSWORD)
                      server.sendmail(settings.MAYA_EMAIL, to_email, msg.as_string())

        logger.info(f"Email sent to {to_email} | Subject: {subject}")
        return True

except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
