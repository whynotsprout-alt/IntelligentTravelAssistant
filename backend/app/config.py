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

    # AMap keys
    amap_web_service_key: str = ""
    amap_js_api_key: str = ""

    # External APIs
    unsplash_access_key: str = ""
    llm_api_key: str = ""
    llm_provider: str = "openai"  # openai | deepseek | compatible
    llm_base_url: str = ""
    llm_model: str = "gpt-4o-mini"


@lru_cache
def get_settings() -> Settings:
    return Settings()
