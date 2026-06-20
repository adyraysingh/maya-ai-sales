"""
config.py - Central settings loaded from environment variables
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
              model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # OpenAI
              OPENAI_API_KEY: str

    # Gmail (maya@makeyourlabel.com via Google Workspace)
              MAYA_EMAIL: str = "maya@makeyourlabel.com"
              GMAIL_APP_PASSWORD: str

    # Zoho CRM (India DC)
              ZOHO_CLIENT_ID: str
              ZOHO_CLIENT_SECRET: str
              ZOHO_REFRESH_TOKEN: str
              ZOHO_BASE_URL: str = "https://www.zohoapis.in/crm/v2"

    # App
              WEBHOOK_SECRET: str = "maya-webhook-secret-2024"


settings = Settings()
