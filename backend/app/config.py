"""Application configuration from environment."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings loaded from env vars."""

    database_url: str = "sqlite+aiosqlite:///./treasure_hunt.db"
    groq_api_key: str = ""
    debug: bool = True
    api_prefix: str = "/api/v1"

    upload_dir: str = "uploads"
    photo_max_age_minutes: int = 60  # Reject photos older than this

    # Sydney bounds for MVP
    sydney_lat_min: float = -34.2
    sydney_lat_max: float = -33.6
    sydney_lon_min: float = 150.5
    sydney_lon_max: float = 151.4

    class Config:
        env_file = ".env"


settings = Settings()
