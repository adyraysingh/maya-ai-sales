"""
webhook/zoho_hook.py - Handle new lead webhook from Zoho CRM
"""

import logging
from fastapi import APIRouter, Request, Header
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/new-lead")
async def new_lead_webhook(
    request: Request,
    x_webhook_secret: str = Header(None),
):
    """
    Receive new lead notification from Zoho CRM.
    WF01 already sends Maya's first email. This just logs the event.
    """
    if x_webhook_secret != settings.WEBHOOK_SECRET:
        logger.warning("Invalid webhook secret - request rejected.")
        return {"status": "unauthorized"}

    try:
        body = await request.json()
        lead_data = body if isinstance(body, dict) else {}
        lead_id = lead_data.get("id", "unknown")
        lead_email = lead_data.get("Email", "unknown")
        first = lead_data.get("First_Name", "")
        last = lead_data.get("Last_Name", "")
        lead_name = f"{first} {last}".strip() or "Unknown"

        logger.info(f"New lead | ID: {lead_id} | Name: {lead_name} | Email: {lead_email}")
        return {"status": "received", "lead_id": lead_id}

    except Exception as e:
        logger.error(f"Error processing new lead webhook: {e}")
        return {"status": "error", "detail": str(e)}
