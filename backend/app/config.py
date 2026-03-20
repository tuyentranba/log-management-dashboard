from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    # Database configuration
    database_url: str = Field(
        validation_alias='DATABASE_URL',
        description="PostgreSQL async connection string"
    )

    # CORS configuration (comma-separated string parsed to list)
    cors_origins: str = Field(
        default="http://localhost:3000",
        validation_alias='CORS_ORIGINS',
        description="Comma-separated list of allowed CORS origins"
    )

    # Server configuration
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into list."""
        return [origin.strip() for origin in self.cors_origins.split(',')]


# Global settings instance
settings = Settings()
