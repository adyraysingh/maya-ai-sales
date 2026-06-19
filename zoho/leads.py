"""
zoho/leads.py - Read lead data from Zoho CRM
"""

import logging
from typing import Optional
from .client import zoho_get

logger = logging.getLogger(__name__)


def get_lead_by_email(email: str) -> Optional[dict]:
      """Find a lead in Zoho CRM by email address."""
      try:
                data = zoho_get(
                              "Leads/search",
                              params={"email": email, "fields": (
                                                "id,First_Name,Last_Name,Email,Lead_Status,"
                                                "Description,Lead_Source,Company,Phone"
                              )},
                )
                records = data.get("data", [])
                if records:
                              return records[0]
                          return None
except Exception as e:
        logger.error(f"Error fetching lead for {email}: {e}")
        return None


def get_lead_by_id(lead_id: str) -> Optional[dict]:
      """Get a single lead record by Zoho CRM ID."""
      try:
                data = zoho_get(f"Leads/{lead_id}")
                records = data.get("data", [])
                return records[0] if records else None
except Exception as e:
        logger.error(f"Error fetching lead {lead_id}: {e}")
        return None


def get_lead_full_name(lead: dict) -> str:
      """Build full name from lead dict."""
      first = lead.get("First_Name", "").strip()
      last = lead.get("Last_Name", "").strip()
      return f"{first} {last}".strip() or "there"


def get_lead_context(lead: dict) -> str:
      """Build a plain-text context string about the lead for the AI prompt."""
      name = get_lead_full_name(lead)
      lines = [f"Lead Name: {name}"]
      if lead.get("Company"):
                lines.append(f"Company: {lead['Company']}")
            if lead.get("Lead_Source"):
                      lines.append(f"Lead Source: {lead['Lead_Source']}")
                  if lead.get("Description"):
                            lines.append(f"Notes: {lead['Description']}")
                        return "\n".join(lines)
