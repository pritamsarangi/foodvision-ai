import json
import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# 1. Locate and load .env file from the repo or backend directory
_CURRENT_FILE = Path(__file__).resolve()
# Check backend/.env (2 levels up) or root .env (3 levels up)
_ENV_PATHS = [
    _CURRENT_FILE.parents[2] / ".env",
    _CURRENT_FILE.parents[3] / ".env",
]
for env_path in _ENV_PATHS:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        break


def _resolve_project_root() -> Path:
    """Finds the root of the foodvision-ai repository in both local and container environments."""
    file_path = Path(__file__).resolve()
    candidates = [
        file_path.parents[2],  # backend/
        file_path.parents[3],  # repo root /
        Path("/app"),          # Docker container WORKDIR
    ]
    for candidate in candidates:
        if (candidate / "ml" / "data" / "splits" / "class_to_index.json").exists():
            return candidate
    return file_path.parents[3] if len(file_path.parents) > 3 else Path("/app")


class Settings(BaseModel):
    # Application Metadata
    app_name: str = "FoodVision AI API"
    app_version: str = "0.1.0"
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))

    # Database
    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "")
    )

    # CORS Origins (parsed from JSON or fallback to sensible dev defaults)
    cors_origins: list[str] = Field(
        default_factory=lambda: json.loads(
            os.getenv(
                "FRONTEND_CORS_ORIGINS",
                '["http://localhost:8080", "http://127.0.0.1:8080", "https://lively-frog-75d6.pritamsarangi70.workers.dev"]',
            ).strip()
        )
    )

    # Upload Limits & Supported Types
    max_image_bytes: int = 10 * 1024 * 1024  # 10 MB
    allowed_image_types: set[str] = {"image/jpeg", "image/png", "image/webp"}

    # ML Model Configuration
    model_version: str = "efficientnet-b0-finetuned-v1"
    project_root: Path = Field(default_factory=_resolve_project_root)

    # JWT & Security
    jwt_secret_key: str = Field(
        default_factory=lambda: os.getenv(
            "JWT_SECRET_KEY",
            "insecure-default-change-me-in-production-secret-key-32chars",
        )
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15  # Short-lived (15 minutes)
    refresh_token_expire_days: int = 7     # Long-lived (7 days)

    # Rate Limiting & Valkey (RESP compatible)
    valkey_url: str = Field(
        default_factory=lambda: os.getenv(
            "VALKEY_URL",
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        )
    )

@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton so configuration is only initialized once."""
    return Settings()


settings = get_settings()