"""Application configuration module."""
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Pydantic settings loaded from environment variables."""

    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API key used for authentication.",
    )
    gemini_model: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model name used for both vision and text generation.",
    )
    max_ingredients: int = Field(
        default=20,
        description="Maximum number of ingredients to request from the model.",
        ge=1,
    )
    temperature: float = Field(
        default=0.6,
        description="Temperature used when generating recipes.",
        ge=0.0,
        le=2.0,
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()


__all__ = ["Settings", "get_settings"]
