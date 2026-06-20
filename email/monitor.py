"""
email/monitor.py - Poll maya@makeyourlabel.com Gmail inbox via IMAP every 60 seconds
"""

import sys
import importlib
import imaplib
import time
import logging
from config import settings

# Load stdlib email module by name to avoid conflict with email/ folder
_email_mod = importlib.import_module("email")
_decode_header = importlib.import_module("email.header").decode_header
_parseaddr = importlib.import_module("email.utils").parseaddr

logger = logging.getLogger(__name__)

SEEN_UIDS_FILE = "/tmp/maya_seen_uids.txt"


def _load_seen_uids() -> set:
    try:
        with open(SEEN_UIDS_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()


def _save_seen_uid(uid: str):
    with open(SEEN_UIDS_FILE, "a") as f:
        f.write(uid + "\n")


def _decode_header_value(value: str) -> str:
    parts = _decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return " ".join(decoded)


def _get_body(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition", ""))
            if ctype == "text/plain" and "attachment" not in disp:
                return part.get_payload(decode=True).decode("utf-8", errors="replace")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                return part.get_payload(decode=True).decode("utf-8", errors="replace")
    else:
        return msg.get_payload(decode=True).decode("utf-8", errors="replace")
    return ""


def fetch_new_emails() -> list:
    results = []
    seen_uids = _load_seen_uids()
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(settings.MAYA_EMAIL, settings.GMAIL_APP_PASSWORD)
        mail.select("INBOX")
        status, data = mail.search(None, "UNSEEN")
        if status != "OK":
            return []
        for uid in data[0].split():
            uid_str = uid.decode()
            if uid_str in seen_uids:
                continue
            status, msg_data = mail.fetch(uid, "(RFC822)")
            if status != "OK":
                continue
            msg = _email_mod.message_from_bytes(msg_data[0][1])
            from_raw = msg.get("From", "")
            from_email = _parseaddr(from_raw)[1].lower()
            from_name = _decode_header_value(_parseaddr(from_raw)[0] or from_raw)
            subject = _decode_header_value(msg.get("Subject", "(no subject)"))
            message_id = msg.get("Message-ID", "")
            body = _get_body(msg)
            if from_email == settings.MAYA_EMAIL.lower():
                _save_seen_uid(uid_str)
                continue
            _save_seen_uid(uid_str)
            results.append({
                "from_email": from_email,
                "from_name": from_name,
                "subject": subject,
                "body": body.strip(),
                "message_id": message_id,
            })
        mail.logout()
    except Exception as e:
        logger.error(f"IMAP fetch error: {e}")
    return results


def start_inbox_monitor(callback):
    logger.info("Starting Gmail IMAP inbox monitor (60s polling)...")
    while True:
        try:
            for email_data in fetch_new_emails():
                logger.info(f"New email from {email_data['from_email']}")
                callback(email_data)
        except Exception as e:
            logger.error(f"Monitor loop error: {e}")
        time.sleep(60)
