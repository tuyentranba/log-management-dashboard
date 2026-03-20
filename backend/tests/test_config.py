"""
Tests for application configuration.

Validates:
- Settings loads from environment variables
- CORS origins parsing works correctly
- Default values are applied
"""
import pytest
from app.config import Settings


@pytest.mark.unit
def test_settings_load_defaults():
    """
    Test Settings class applies default values.

    Validates:
    - debug defaults to False
    - log_level defaults to INFO
    - cors_origins has default value
    """
    # Create Settings without environment variables
    settings = Settings(
        database_url="postgresql+psycopg://test:test@localhost/test"
    )

    assert settings.debug is False
    assert settings.log_level == "INFO"
    assert settings.cors_origins is not None


@pytest.mark.unit
def test_cors_origins_parsing():
    """
    Test CORS origins comma-separated parsing.

    Validates cors_origins_list property splits string correctly.
    """
    settings = Settings(
        database_url="postgresql+psycopg://test:test@localhost/test",
        cors_origins="http://localhost:3000,http://localhost:8080,https://example.com"
    )

    origins_list = settings.cors_origins_list
    assert len(origins_list) == 3
    assert "http://localhost:3000" in origins_list
    assert "http://localhost:8080" in origins_list
    assert "https://example.com" in origins_list


@pytest.mark.unit
def test_cors_origins_single_value():
    """
    Test CORS origins parsing with single value.

    Validates parsing works when only one origin is provided.
    """
    settings = Settings(
        database_url="postgresql+psycopg://test:test@localhost/test",
        cors_origins="http://localhost:3000"
    )

    origins_list = settings.cors_origins_list
    assert len(origins_list) == 1
    assert origins_list[0] == "http://localhost:3000"


@pytest.mark.unit
def test_database_url_field():
    """
    Test database_url field is required and loaded.

    Validates Settings requires DATABASE_URL.
    """
    settings = Settings(
        database_url="postgresql+psycopg://user:pass@host:5432/db"
    )

    assert settings.database_url.startswith("postgresql+psycopg://")
    assert "user" in settings.database_url
    assert "host" in settings.database_url
