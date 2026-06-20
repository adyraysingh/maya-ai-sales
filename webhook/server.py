"""
webhook/server.py - FastAPI app + inbox monitor thread
"""

import os
import sys
import logging
import threading
import importlib.util
from contextlib import asynccontextmanager
from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Resolve repo root (one level up from webhook/)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_module(name, path):
    """Load a Python file as a module by absolute path."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _run_inbox_monitor():
    """Background thread: poll Gmail inbox and reply with Maya."""
    try:
        monitor = _load_module("mail_monitor", os.path.join(ROOT, "email", "monitor.py"))
        sender = _load_module("mail_sender", os.path.join(ROOT, "email", "sender.py"))

        from ai.response import generate_maya_response, wrap_reply_in_html

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
                re_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"
                sender.send_email(
                    to_email=from_email,
                    to_name=from_name,
                    subject=re_subject,
                    body_html=reply_html,
                    reply_to_message_id=message_id,
                )
                logger.info(f"Reply sent to {from_email}")
            except Exception as exc:
                logger.error(f"Error handling email: {exc}")

        monitor.start_inbox_monitor(on_new_email)

    except Exception as exc:
        logger.error(f"Inbox monitor failed to start: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Maya AI Sales Engine starting...")
    t = threading.Thread(target=_run_inbox_monitor, daemon=True)
    t.start()
    logger.info("Inbox monitor thread started (60s polling).")
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
