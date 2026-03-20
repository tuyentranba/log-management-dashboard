"""
Unit tests for Pydantic schemas.

Tests log request/response validation, timezone enforcement, and ORM compatibility.
"""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.schemas.logs import LogCreate, LogResponse, LogListResponse
from app.models import Log


def test_log_create_valid():
    """
    Test LogCreate validation with valid data.

    Verifies timezone-aware timestamp and valid severity are accepted.
    """
    log_data = {
        "timestamp": datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc),
        "message": "Test log message",
        "severity": "ERROR",
        "source": "test-service"
    }

    log = LogCreate(**log_data)

    assert log.timestamp == log_data["timestamp"]
    assert log.message == log_data["message"]
    assert log.severity == "ERROR"
    assert log.source == "test-service"


def test_log_create_no_timezone():
    """
    Test LogCreate rejects timestamp without timezone.

    Should raise ValidationError for timezone-naive timestamps.
    """
    with pytest.raises(ValidationError, match="timezone"):
        LogCreate(
            timestamp="2024-03-20T15:30:00",  # No timezone
            message="Test message",
            severity="INFO",
            source="test"
        )


def test_log_create_invalid_severity():
    """
    Test LogCreate rejects invalid severity values.

    Should raise ValidationError for severity not in enum.
    """
    with pytest.raises(ValidationError):
        LogCreate(
            timestamp=datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc),
            message="Test message",
            severity="INVALID",  # Not in enum
            source="test"
        )


def test_log_create_valid_severities():
    """
    Test LogCreate accepts all valid severity values.

    Verifies INFO, WARNING, ERROR, CRITICAL are all accepted.
    """
    valid_severities = ["INFO", "WARNING", "ERROR", "CRITICAL"]

    for severity in valid_severities:
        log = LogCreate(
            timestamp=datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc),
            message="Test message",
            severity=severity,
            source="test"
        )
        assert log.severity == severity


def test_log_create_empty_message():
    """
    Test LogCreate rejects empty message.

    Should raise ValidationError for min_length=1 constraint.
    """
    with pytest.raises(ValidationError):
        LogCreate(
            timestamp=datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc),
            message="",  # Empty message
            severity="INFO",
            source="test"
        )


def test_log_create_empty_source():
    """
    Test LogCreate rejects empty source.

    Should raise ValidationError for min_length=1 constraint.
    """
    with pytest.raises(ValidationError):
        LogCreate(
            timestamp=datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc),
            message="Test message",
            severity="INFO",
            source=""  # Empty source
        )


def test_log_response_from_orm():
    """
    Test LogResponse can be created from SQLAlchemy Log model.

    Verifies ORM compatibility with from_attributes=True.
    """
    # Create Log model instance
    log = Log(
        id=123,
        timestamp=datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc),
        message="Test log message",
        severity="ERROR",
        source="test-service"
    )

    # Validate with LogResponse
    response = LogResponse.model_validate(log)

    assert response.id == 123
    assert response.timestamp == log.timestamp
    assert response.message == "Test log message"
    assert response.severity == "ERROR"
    assert response.source == "test-service"


def test_log_list_response_structure():
    """
    Test LogListResponse validates and serializes correctly.

    Verifies structure with list of logs, cursor, and has_more flag.
    """
    log1 = LogResponse(
        id=1,
        timestamp=datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc),
        message="Log 1",
        severity="INFO",
        source="service-1"
    )
    log2 = LogResponse(
        id=2,
        timestamp=datetime(2024, 3, 20, 16, 30, 0, tzinfo=timezone.utc),
        message="Log 2",
        severity="ERROR",
        source="service-2"
    )

    response = LogListResponse(
        data=[log1, log2],
        next_cursor="cursor123",
        has_more=True
    )

    assert len(response.data) == 2
    assert response.data[0].id == 1
    assert response.data[1].id == 2
    assert response.next_cursor == "cursor123"
    assert response.has_more is True

    # Test with null cursor
    response_no_more = LogListResponse(
        data=[log1],
        next_cursor=None,
        has_more=False
    )

    assert response_no_more.next_cursor is None
    assert response_no_more.has_more is False


def test_log_response_timezone_preserved():
    """
    Test LogResponse preserves timezone in JSON serialization.

    Verifies timestamp includes timezone suffix in output.
    """
    response = LogResponse(
        id=1,
        timestamp=datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc),
        message="Test message",
        severity="INFO",
        source="test"
    )

    json_str = response.model_dump_json()

    # JSON should contain timezone indicator (Z or +00:00)
    assert "Z" in json_str or "+00:00" in json_str
    assert "2024-03-20" in json_str
