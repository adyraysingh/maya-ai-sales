"""
email/graph_client.py - Microsoft Graph API authentication and base HTTP client
Uses client credentials flow (app-only) to access maya@makeyourlabel.com mailbox
"""

import httpx
import time
import logging
from config import settings

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

_token_cache = {"access_token": None, "expires_at": 0}


def _get_graph_token() -> str:
      """Get a valid Microsoft Graph access token using client credentials."""
      now = time.time()
      if _token_cache["access_token"] and now < _token_cache["expires_at"] - 60:
                return _token_cache["access_token"]

      token_url = (
          f"https://login.microsoftonline.com/"
          f"{settings.microsoft_tenant_id}/oauth2/v2.0/token"
      )
      payload = {
          "client_id": settings.microsoft_client_id,
          "client_secret": settings.microsoft_client_secret,
          "scope": "https://graph.microsoft.com/.default",
          "grant_type": "client_credentials",
      }

    with httpx.Client(timeout=15) as client:
              resp = client.post(token_url, data=payload)
              resp.raise_for_status()
              data = resp.json()

    if "access_token" not in data:
              raise RuntimeError(f"Graph token request failed: {data}")

    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = now + data.get("expires_in", 3600)
    return _token_cache["access_token"]


def graph_get(endpoint: str, params: dict = None) -> dict:
      token = _get_graph_token()
      with httpx.Client(timeout=30) as client:
                resp = client.get(
                              f"{GRAPH_BASE}/{endpoint}",
                              headers={"Authorization": f"Bearer {token}"},
                              params=params
                )
                resp.raise_for_status()
                return resp.json()


def graph_post(endpoint: str, payload: dict) -> dict:
      token = _get_graph_token()
      with httpx.Client(timeout=30) as client:
                resp = client.post(
                              f"{GRAPH_BASE}/{endpoint}",
                              headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                              json=payload
                )
                resp.raise_for_status()
                try:
                              return resp.json()
except Exception:
            return {"status": resp.status_code}


def graph_patch(endpoint: str, payload: dict) -> dict:
      token = _get_graph_token()
      with httpx.Client(timeout=30) as client:
                resp = client.patch(
                              f"{GRAPH_BASE}/{endpoint}",
                              headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                              json=payload
                )
                resp.raise_for_status()
                try:
                              return resp.json()
except Exception:
            return {"status": resp.status_code}


def graph_delete(endpoint: str) -> int:
      token = _get_graph_token()
      with httpx.Client(timeout=30) as client:
                resp = client.delete(
                              f"{GRAPH_BASE}/{endpoint}",
                              headers={"Authorization": f"Bearer {token}"}
                )
                resp.raise_for_status()
                return resp.status_code
