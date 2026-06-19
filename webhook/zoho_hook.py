""
webhook/zoho_hook.py - Handle new lead webhook from Zoho CRM
When Zoho fires a webhook for a new lead, we log it.
The AI conversation starts only when the prospect replies to Maya's first email.
(Maya's first email is sent by WF01 in Zoho CRM directly.)
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
    Validates the webhook secret and logs the new lead.

    Zoho WF01 already sends Maya's first email automatically.
    This endpoint just logs the event for audit purposes.
    """
    # Validate webhook secret
    if x_webhook_secret != settings.webhook_secret:
        logger.warning("Invalid webhook secret received - request rejected.")
        return {"status": "unauthorized"}

    try:
        body = await request.json()
        lead_data = body if isinstance(body, dict) else {}

        lead_id = lead_data.get("id", "unknown")
        lead_email = lead_data.get("Email", "unknown")
        lead_name = (
            f"{lead_data.get('First_Name', '')} {lead_data.get('Last_Name', '')}".strip()
            or "Unknown"
        )

        logger.info(
            f"New lead received | ID: {lead_id} | "
            f"Name: {lead_name} | Email: {lead_email}"
        )

        return {
            "status": "received",
            "lead_id": lead_id,
            "message": "Lead logged. WF01 will send first email."
        }

    except Exception as e:
        logger.error(f"Error processing new lead webhook: {e}")
        return {"status": "error", "detail": str(e)}
