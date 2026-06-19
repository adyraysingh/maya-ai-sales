""
zoho/summary.py - Write conversation summary back to Zoho CRM lead record
"""

import logging
from datetime import datetime
from .client import zoho_put

logger = logging.getLogger(__name__)


def update_lead_summary(lead_id: str, summary: str) -> bool:
    """
    Write the AI conversation summary to the Description field of a Zoho lead.
    Prepends timestamp so history is preserved.
    Returns True on success, False on failure.
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    tagged_summary = f"[Maya AI - {timestamp}]\n{summary}"

    payload = {
        "data": [
            {
                "id": lead_id,
                "Description": tagged_summary,
            }
        ]
    }

    try:
        result = zoho_put("Leads", payload)
        status = result.get("data", [{}])[0].get("code", "")
        if status == "SUCCESS":
            logger.info(f"Summary updated for lead {lead_id}")
            return True
        else:
            logger.warning(f"Unexpected result updating lead {lead_id}: {result}")
            return False
    except Exception as e:
        logger.error(f"Failed to update summary for lead {lead_id}: {e}")
        return False


def append_to_lead_notes(lead_id: str, existing_notes: str, new_entry: str) -> bool:
    """
    Append a new conversation entry to existing notes rather than overwriting.
    Keeps the full conversation log in the Description field.
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    separator = "\n" + "-" * 40 + "\n"
    new_note = f"{separator}[{timestamp}]\n{new_entry}"

    updated = (existing_notes or "") + new_note
    # Zoho Description field limit is 32000 characters; truncate if needed
    if len(updated) > 31000:
        updated = updated[-31000:]

    payload = {
        "data": [
            {
                "id": lead_id,
                "Description": updated,
            }
        ]
    }

    try:
        result = zoho_put("Leads", payload)
        status = result.get("data", [{}])[0].get("code", "")
        return status == "SUCCESS"
    except Exception as e:
        logger.error(f"Failed to append notes for lead {lead_id}: {e}")
        return False
