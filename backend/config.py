"""
config.py — Application Settings
Loads all environment variables via Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────
    app_name: str = "EnterpriseLead AI"
    debug: bool = Field(default=False, env="DEBUG")
    port: int = Field(default=8000, env="PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # ── Database ─────────────────────────────────
    database_url: str = Field(..., env="DATABASE_URL")

    # ── Claude API ───────────────────────────────
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    claude_model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 1024

    # ── HubSpot ──────────────────────────────────
    hubspot_api_key: str = Field(default="", env="HUBSPOT_API_KEY")

    # ── Alerts ───────────────────────────────────
    lead_score_threshold: int = Field(default=75, env="LEAD_SCORE_THRESHOLD")
    twilio_account_sid: str = Field(default="", env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(default="", env="TWILIO_AUTH_TOKEN")
    twilio_phone_from: str = Field(default="", env="TWILIO_PHONE_FROM")
    sales_alert_phone: str = Field(default="", env="SALES_ALERT_PHONE")
    sendgrid_api_key: str = Field(default="", env="SENDGRID_API_KEY")
    sales_email: str = Field(default="", env="SALES_EMAIL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loaded once at startup."""
    return Settings()


settings = get_settings()
