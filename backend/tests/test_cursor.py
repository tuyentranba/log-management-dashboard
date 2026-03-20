"""
Unit tests for cursor encoding/decoding utilities.

Tests base64 encoding, decoding validation, and roundtrip consistency.
"""
import pytest
import base64
import json
from datetime import datetime, timezone

from app.utils.cursor import encode_cursor, decode_cursor


def test_encode_cursor_valid():
    """
    Test encoding cursor with valid timestamp and id.

    Verifies that encode_cursor returns base64 string containing
    timestamp and id fields in JSON format.
    """
    timestamp = datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc)
    log_id = 123

    cursor = encode_cursor(timestamp, log_id)

    # Verify it's a base64 string
    assert isinstance(cursor, str)

    # Decode and verify structure
    decoded_json = base64.b64decode(cursor.encode()).decode()
    cursor_data = json.loads(decoded_json)

    assert "timestamp" in cursor_data
    assert "id" in cursor_data
    assert cursor_data["id"] == 123


def test_decode_cursor_valid():
    """
    Test decoding valid cursor from encode_cursor.

    Verifies decode_cursor returns tuple matching original values.
    """
    timestamp = datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc)
    log_id = 123

    cursor = encode_cursor(timestamp, log_id)
    decoded_timestamp, decoded_id = decode_cursor(cursor)

    assert decoded_id == log_id
    assert decoded_timestamp == timestamp


def test_decode_cursor_invalid_base64():
    """
    Test decode_cursor with invalid base64 string.

    Should raise ValueError with clear error message.
    """
    with pytest.raises(ValueError, match="Invalid cursor token"):
        decode_cursor("not-base64!!!")


def test_decode_cursor_invalid_json():
    """
    Test decode_cursor with base64 of non-JSON data.

    Should raise ValueError when JSON parsing fails.
    """
    # Encode non-JSON data
    invalid_cursor = base64.b64encode(b"not json data").decode()

    with pytest.raises(ValueError, match="Invalid cursor token"):
        decode_cursor(invalid_cursor)


def test_decode_cursor_missing_fields():
    """
    Test decode_cursor with JSON missing required fields.

    Should raise ValueError when timestamp or id is missing.
    """
    # Missing timestamp field
    cursor_data = {"id": 123}
    cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

    with pytest.raises(ValueError, match="Invalid cursor token"):
        decode_cursor(cursor)

    # Missing id field
    cursor_data = {"timestamp": "2024-03-20T15:30:00+00:00"}
    cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

    with pytest.raises(ValueError, match="Invalid cursor token"):
        decode_cursor(cursor)


def test_encode_decode_roundtrip():
    """
    Test encode then decode returns exact original values.

    Verifies roundtrip consistency with multiple timestamp/id combinations.
    """
    test_cases = [
        (datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc), 123),
        (datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc), 1),
        (datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc), 999999),
    ]

    for original_timestamp, original_id in test_cases:
        cursor = encode_cursor(original_timestamp, original_id)
        decoded_timestamp, decoded_id = decode_cursor(cursor)

        assert decoded_timestamp == original_timestamp
        assert decoded_id == original_id


def test_cursor_opaque():
    """
    Test that encoded cursor doesn't contain readable timestamp or id.

    Validates base64 encoding obscures the data.
    """
    timestamp = datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc)
    log_id = 123

    cursor = encode_cursor(timestamp, log_id)

    # Cursor should not contain plain text year or id
    assert "2024" not in cursor
    assert "123" not in cursor
    # Base64 encoding ensures opacity
    assert len(cursor) > 20  # Reasonably long base64 string
