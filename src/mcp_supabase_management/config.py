"""Pydantic Settings configuration for Supabase Management MCP server."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Supabase Management API configuration.

    Reads from environment variables with SUPABASE_ prefix or .env file.
    """

    access_token: str = Field(description="Supabase Management API access token (sbp_*)")

    model_config = SettingsConfigDict(
        env_prefix="SUPABASE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Get configuration from environment variables or .env file."""
    return Settings()
