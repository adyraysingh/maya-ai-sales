"""
zoho/client.py - Zoho CRM REST API client with auto token refresh
"""

import requests
import time
import logging
from config import settings

logger = logging.getLogger(__name__)

_token_cache = {"access_token": None, "expires_at": 0}


def _get_access_token() -> str:
          now = time.time()
          if _token_cache["access_token"] and now < _token_cache["expires_at"] - 60:
                        return _token_cache["access_token"]
                    resp = requests.post(
                                  "https://accounts.zoho.in/oauth/v2/token",
                                  params={
                                                    "refresh_token": settings.ZOHO_REFRESH_TOKEN,
                                                    "client_id": settings.ZOHO_CLIENT_ID,
                                                    "client_secret": settings.ZOHO_CLIENT_SECRET,
                                                    "grant_type": "refresh_token",
                                  },
                                  timeout=15,
                    )
    resp.raise_for_status()
    data = resp.json()
    if "access_token" not in data:
                  raise RuntimeError(f"Zoho token refresh failed: {data}")
              _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = now + data.get("expires_in", 3600)
    return _token_cache["access_token"]


def _headers() -> dict:
          return {
              "Authorization": f"Zoho-oauthtoken {_get_access_token()}",
              "Content-Type": "application/json",
}


def zoho_get(endpoint: str, params: dict = None) -> dict:
          resp = requests.get(
              f"{settings.ZOHO_BASE_URL}/{endpoint}",
              headers=_headers(), params=params, timeout=15
)
    resp.raise_for_status()
    return resp.json()


def zoho_put(endpoint: str, payload: dict) -> dict:
          resp = requests.put(
              f"{settings.ZOHO_BASE_URL}/{endpoint}",
              headers=_headers(), json=payload, timeout=15
)
    resp.raise_for_status()
    return resp.json()


def zoho_post(endpoint: str, payload: dict) -> dict:
          resp = requests.post(
              f"{settings.ZOHO_BASE_URL}/{endpoint}",
              headers=_headers(), json=payload, timeout=15
)
    resp.raise_for_status()
    return resp.json()
