"""
Tests for application configuration.

Validates:
- Settings loads from environment variables
- CORS origins parsing works correctly
- Default values are applied
"""
import pytest
import os
from app.config import Settings


@pytest.mark.unit
def test_settings_load_defaults(monkeypatch):
    """
    Test Settings class applies default values.

    Validates:
    - debug defaults to False
    - log_level defaults to INFO
    - cors_origins has default value
    """
    # Create Settings with environment variable
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")
    settings = Settings()

    assert settings.debug is False
    assert settings.log_level == "INFO"
    assert settings.cors_origins is not None


@pytest.mark.unit
def test_cors_origins_parsing(monkeypatch):
    """
    Test CORS origins comma-separated parsing.

    Validates cors_origins_list property splits string correctly.
    """
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080,https://example.com")
    settings = Settings()

    origins_list = settings.cors_origins_list
    assert len(origins_list) == 3
    assert "http://localhost:3000" in origins_list
    assert "http://localhost:8080" in origins_list
    assert "https://example.com" in origins_list


@pytest.mark.unit
def test_cors_origins_single_value(monkeypatch):
    """
    Test CORS origins parsing with single value.

    Validates parsing works when only one origin is provided.
    """
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
    settings = Settings()

    origins_list = settings.cors_origins_list
    assert len(origins_list) == 1
    assert origins_list[0] == "http://localhost:3000"


@pytest.mark.unit
def test_database_url_field(monkeypatch):
    """
    Test database_url field is required and loaded.

    Validates Settings requires DATABASE_URL.
    """
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@host:5432/db")
    settings = Settings()

    assert settings.database_url.startswith("postgresql+psycopg://")
    assert "user" in settings.database_url
    assert "host" in settings.database_url
