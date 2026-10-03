"""Application configuration module."""

import os
import socket
import uuid
from functools import lru_cache

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:  # Fallback if pydantic-settings not yet installed
    from pydantic import BaseModel as BaseSettings
    SettingsConfigDict = None


class Settings(BaseSettings):
    """Application runtime settings."""

    if SettingsConfigDict is not None:
        model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SERVICE_NAME: str = "CloudPulse Microservice"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Instance ID for distributed tracking and load balancing demonstration
    INSTANCE_ID: str = os.getenv(
        "INSTANCE_ID",
        os.getenv("HOSTNAME", f"node-{socket.gethostname()}-{uuid.uuid4().hex[:6]}")
    )

    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


@lru_cache()
def get_settings() -> Settings:
    """Retrieve cached application settings."""
    return Settings()
