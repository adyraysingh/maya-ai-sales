"""
webhook/server.py - FastAPI application entry point
Handles Zoho CRM webhooks and runs the email polling scheduler
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from config import settings
from .zoho_hook import router as zoho_router
from webhook.email_loop import process_new_emails

logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
      """Start scheduler on startup, shut down on exit."""
      logger.info("Maya AI Sales Engine starting up...")

    # Poll inbox every 60 seconds for new replies
      scheduler.add_job(
          process_new_emails,
          trigger="interval",
          seconds=60,
          id="email_poller",
          replace_existing=True,
      )
      scheduler.start()
      logger.info("Email polling scheduler started (every 60 seconds).")

    yield

    scheduler.shutdown(wait=False)
    logger.info("Maya AI Sales Engine shutting down.")


app = FastAPI(
      title="Maya AI Sales Engine",
      description="Autonomous AI sales consultant for MakeYourLabel",
      version="1.0.0",
      lifespan=lifespan,
)

# Register webhook routes
app.include_router(zoho_router, prefix="/webhook", tags=["Webhooks"])


@app.get("/health")
async def health_check():
      """Simple health check endpoint."""
      return {"status": "ok", "service": "maya-ai-sales"}
