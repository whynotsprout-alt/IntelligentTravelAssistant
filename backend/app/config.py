"""Application configuration (env / defaults)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Intelligent Travel Assistant API"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # External APIs (set via environment)
    amap_api_key: str = ""
    unsplash_access_key: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
