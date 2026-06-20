"""
webhook/server.py - FastAPI app entry point
"""

import logging
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from email.monitor import start_inbox_monitor
from ai.responder import handle_reply

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def _on_new_email(email_data: dict):
    """Called for each new email from the inbox monitor."""
    try:
        handle_reply(email_data)
    except Exception as e:
        logger.error(f"Error handling email: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Maya AI Sales Engine starting up...")
    t = threading.Thread(
        target=start_inbox_monitor,
        args=(_on_new_email,),
        daemon=True,
    )
    t.start()
    logger.info("Inbox monitor thread started.")
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
