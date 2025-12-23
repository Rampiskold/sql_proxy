from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Database configuration
    database_url: str = Field(
        description="PostgreSQL connection URL",
        examples=["postgresql://user:pass@localhost:5432/dbname"],
    )
    db_schema: str = Field(
        default="public",
        description="PostgreSQL schema name to use for queries",
    )

    # Connection pool settings
    db_pool_min_size: int = Field(default=5, ge=1, le=100)
    db_pool_max_size: int = Field(default=20, ge=1, le=100)
    db_pool_timeout: float = Field(default=30.0, ge=1.0)

    # API settings
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=18790, ge=1, le=65535)

    # Logging
    log_level: str = Field(default="INFO")


# Singleton instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get settings singleton instance."""
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]
    return _settings
