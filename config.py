"""
config.py - Centralised settings for Maya AI Sales Engine
All values loaded from .env via pydantic-settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
      # OpenAI
      openai_api_key: str

    # Microsoft Graph (maya@makeyourlabel.com)
      microsoft_tenant_id: str
      microsoft_client_id: str
      microsoft_client_secret: str
      maya_email: str = "maya@makeyourlabel.com"

    # Zoho CRM
      zoho_client_id: str
      zoho_client_secret: str
      zoho_refresh_token: str
      zoho_base_url: str = "https://www.zohoapis.in/crm/v2"
      zoho_org_id: str = "60057163213"

    # App
      app_host: str = "0.0.0.0"
      app_port: int = 8000
      app_env: str = "production"

    # Security
      webhook_secret: str

    # Conversation
      max_conversation_turns: int = 20
      response_delay_seconds: int = 30

    class Config:
              env_file = ".env"
              env_file_encoding = "utf-8"
              case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
      """Return cached settings instance."""
      return Settings()


# Convenience alias
settings = get_settings()
