"""
webhook/server.py - FastAPI app entry point
"""

import logging
import threading
import importlib
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def _run_inbox_monitor():
    """Import and run the inbox monitor in a background thread."""
    # Use importlib to avoid conflict with Python's built-in email module
    monitor = importlib.import_module("email.monitor")
    from ai.response import generate_maya_response, wrap_reply_in_html
    from email_module.sender import send_email

    def on_new_email(email_data: dict):
        try:
            from_email = email_data["from_email"]
            from_name = email_data["from_name"]
            subject = email_data["subject"]
            body = email_data["body"]
            message_id = email_data.get("message_id", "")

            reply_text = generate_maya_response(
                prospect_email=from_email,
                prospect_message=body,
            )
            reply_html = wrap_reply_in_html(reply_text)

            re_subject = subject if subject.startswith("Re:") else f"Re: {subject}"
            send_email(
                to_email=from_email,
                to_name=from_name,
                subject=re_subject,
                body_html=reply_html,
                reply_to_message_id=message_id,
            )
            logger.info(f"Reply sent to {from_email}")
        except Exception as e:
            logger.error(f"Error handling email from {email_data.get('from_email')}: {e}")

    monitor.start_inbox_monitor(on_new_email)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Maya AI Sales Engine starting up...")
    t = threading.Thread(target=_run_inbox_monitor, daemon=True)
    t.start()
    logger.info("Inbox monitor thread started (polling every 60s).")
    yield
    logger.info("Maya AI Sales Engine shutting down.")


app = FastAPI(
    title="Maya AI Sales Engine",
    description="Autonomous AI sales consultant for MakeYourLabel",
    version="1.0.0",
    lifespan=lifespan,
)

from .zoho_hook import router as zoho_router  # noqa: E402
app.include_router(zoho_router, prefix="/webhook", tags=["Webhooks"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "maya-ai-sales"}
