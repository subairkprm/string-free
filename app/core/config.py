from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """String Free application settings.
    All values loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Supabase
    supabase_url: AnyUrl = Field(default="https://placeholder.supabase.co", alias="SUPABASE_URL")
    supabase_key: str = Field(default="", alias="SUPABASE_KEY")

    # Google Gemini AI
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")

    # Telegram Bot
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", alias="TELEGRAM_CHAT_ID")

    # Sentry Error Tracking
    sentry_dsn: str | None = Field(default=None, alias="SENTRY_DSN")

    # Lemon Squeezy Billing
    lemon_squeezy_webhook_secret: str = Field(default="", alias="LEMON_SQUEEZY_WEBHOOK_SECRET")
    lemon_squeezy_solo_variant_id: str = Field(default="", alias="LEMON_SQUEEZY_SOLO_VARIANT_ID")
    lemon_squeezy_pro_variant_id: str = Field(default="", alias="LEMON_SQUEEZY_PRO_VARIANT_ID")
    lemon_squeezy_team_variant_id: str = Field(default="", alias="LEMON_SQUEEZY_TEAM_VARIANT_ID")

    # Application
    environment: str = Field(default="local", alias="ENVIRONMENT")
    ai_delay_seconds: int = Field(default=4, alias="AI_DELAY_SECONDS")


settings = Settings()  # type: ignore[call-arg]
