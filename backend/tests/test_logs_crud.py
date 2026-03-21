"""
Integration tests for log CRUD endpoints.

Tests POST /api/logs (create) and GET /api/logs/{id} (read single).
"""
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Log


# ============================================================================
# POST /api/logs - Create log endpoint tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_log_success(client: AsyncClient):
    """POST /api/logs with valid data returns 201 with created log."""
    log_data = {
        "timestamp": "2024-03-20T15:30:00Z",
        "message": "Test log message",
        "severity": "INFO",
        "source": "test-service"
    }

    response = await client.post("/api/logs", json=log_data)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["message"] == "Test log message"
    assert data["severity"] == "INFO"
    assert data["source"] == "test-service"
    # Verify timestamp preserved with timezone
    assert "Z" in data["timestamp"] or "+00:00" in data["timestamp"]


@pytest.mark.asyncio
async def test_create_log_missing_timestamp(client: AsyncClient):
    """POST /api/logs without timestamp field returns 400."""
    log_data = {
        "message": "Test message",
        "severity": "INFO",
        "source": "test-service"
    }

    response = await client.post("/api/logs", json=log_data)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_log_missing_message(client: AsyncClient):
    """POST /api/logs without message field returns 400."""
    log_data = {
        "timestamp": "2024-03-20T15:30:00Z",
        "severity": "INFO",
        "source": "test-service"
    }

    response = await client.post("/api/logs", json=log_data)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_log_timezone_naive(client: AsyncClient):
    """POST /api/logs with timezone-naive timestamp returns 400."""
    log_data = {
        "timestamp": "2024-03-20T15:30:00",  # No timezone indicator
        "message": "Test message",
        "severity": "INFO",
        "source": "test-service"
    }

    response = await client.post("/api/logs", json=log_data)

    assert response.status_code == 400
    response_text = response.text.lower()
    assert "timezone" in response_text


@pytest.mark.asyncio
async def test_create_log_invalid_severity(client: AsyncClient):
    """POST /api/logs with invalid severity returns 400."""
    log_data = {
        "timestamp": "2024-03-20T15:30:00Z",
        "message": "Test message",
        "severity": "INVALID",
        "source": "test-service"
    }

    response = await client.post("/api/logs", json=log_data)

    assert response.status_code == 400
    response_text = response.text.lower()
    assert "severity" in response_text


@pytest.mark.asyncio
async def test_create_log_empty_message(client: AsyncClient):
    """POST /api/logs with empty message returns 400."""
    log_data = {
        "timestamp": "2024-03-20T15:30:00Z",
        "message": "",
        "severity": "INFO",
        "source": "test-service"
    }

    response = await client.post("/api/logs", json=log_data)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_log_empty_source(client: AsyncClient):
    """POST /api/logs with empty source returns 400."""
    log_data = {
        "timestamp": "2024-03-20T15:30:00Z",
        "message": "Test message",
        "severity": "INFO",
        "source": ""
    }

    response = await client.post("/api/logs", json=log_data)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_log_persisted(client: AsyncClient, test_db: AsyncSession):
    """POST /api/logs persists log to database."""
    log_data = {
        "timestamp": "2024-03-20T15:30:00Z",
        "message": "Persistence test",
        "severity": "WARNING",
        "source": "test-service"
    }

    response = await client.post("/api/logs", json=log_data)

    assert response.status_code == 201
    created_id = response.json()["id"]

    # Query database directly to verify log exists
    result = await test_db.execute(select(Log).where(Log.id == created_id))
    db_log = result.scalar_one_or_none()

    assert db_log is not None
    assert db_log.message == "Persistence test"
    assert db_log.severity == "WARNING"
    assert db_log.source == "test-service"


@pytest.mark.asyncio
async def test_create_log_all_severities(client: AsyncClient):
    """POST /api/logs succeeds for all valid severity levels."""
    severities = ["INFO", "WARNING", "ERROR", "CRITICAL"]

    for severity in severities:
        log_data = {
            "timestamp": "2024-03-20T15:30:00Z",
            "message": f"Test {severity} log",
            "severity": severity,
            "source": "test-service"
        }

        response = await client.post("/api/logs", json=log_data)

        assert response.status_code == 201, f"Failed for severity {severity}"
        assert response.json()["severity"] == severity
