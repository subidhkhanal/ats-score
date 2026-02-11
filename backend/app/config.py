from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    gemini_api_key: str = ""
    model_cache_dir: str = "./models"
    cors_origins: str = "http://localhost:3000,https://*.vercel.app,https://*.hf.space"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
