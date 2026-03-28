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
    supabase_url: AnyUrl = Field(alias="SUPABASE_URL")
    supabase_key: str = Field(alias="SUPABASE_KEY")

    # Google Gemini AI
    gemini_api_key: str = Field(alias="GEMINI_API_KEY")

    # Telegram Bot
    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(alias="TELEGRAM_CHAT_ID")

    # Sentry Error Tracking
    sentry_dsn: str | None = Field(default=None, alias="SENTRY_DSN")

    # Application
    environment: str = Field(default="local", alias="ENVIRONMENT")
    ai_delay_seconds: int = Field(default=4, alias="AI_DELAY_SECONDS")


settings = Settings()  # type: ignore[call-arg]
