from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    wise_api_base_url: str = "https://api.transferwise.com"
    wise_api_key: str | None = None

    cache_ttl_seconds: int = 300  # 5 minutes

    api_prefix: str = "/api/v1"
    app_name: str = "PH Remittance Rates API"
    app_version: str = "1.0.0"

    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
