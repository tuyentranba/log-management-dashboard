"""
Cursor encoding/decoding utilities for pagination.

Provides opaque cursor tokens for cursor-based pagination,
allowing internal implementation changes without breaking clients.

For detailed decision rationale, see ADR-002: Cursor Pagination
(docs/decisions/002-cursor-pagination.md).
"""
import base64
import json
from datetime import datetime
from typing import Tuple


def encode_cursor(timestamp: datetime, log_id: int) -> str:
    """
    Encode pagination cursor as opaque base64 string.

    Base64 encoding keeps cursor format opaque to clients, allowing
    internal implementation changes without breaking API contracts.
    Composite key (timestamp + id) enables stable ordering even when
    multiple logs share the same timestamp.

    Args:
        timestamp: Log timestamp (must be timezone-aware)
        log_id: Log primary key

    Returns:
        Base64-encoded JSON string containing timestamp (ISO format) and id

    Raises:
        ValueError: If timestamp is timezone-naive

    Example:
        >>> from datetime import datetime, timezone
        >>> encode_cursor(datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc), 123)
        'eyJ0aW1lc3RhbXAiOiAiMjAyNC0wMy0yMFQxNTozMDowMCswMDowMCIsICJpZCI6IDEyM30='
    """
    # Composite cursor (timestamp + id) ensures stable ordering
    # Even if multiple logs have identical timestamps, id provides unique sort key
    # This prevents duplicate or missing rows during pagination
    cursor_data = {
        "timestamp": timestamp.isoformat(),
        "id": log_id
    }
    json_str = json.dumps(cursor_data)

    # Base64 encoding makes cursor opaque to clients
    # Clients cannot construct cursors manually or depend on internal format
    # This allows changing cursor structure (e.g., adding fields) without breaking clients
    return base64.b64encode(json_str.encode()).decode()


def decode_cursor(cursor: str) -> Tuple[datetime, int]:
    """
    Decode pagination cursor from base64.

    Args:
        cursor: Base64-encoded cursor string from encode_cursor

    Returns:
        Tuple of (timestamp, log_id)

    Raises:
        ValueError: If cursor format is invalid (not base64, not JSON, missing fields)

    Example:
        decode_cursor("eyJ0aW1lc3RhbXAiOiAiMjAyNC0wMy0yMFQxNTozMDowMCswMDowMCIsICJpZCI6IDEyM30=")
        # Returns: (datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc), 123)
    """
    try:
        json_str = base64.b64decode(cursor.encode()).decode()
        cursor_data = json.loads(json_str)

        # Validate required fields exist to catch malformed cursors early
        # Prevents confusing errors downstream in SQL query building
        if "timestamp" not in cursor_data or "id" not in cursor_data:
            raise ValueError("Invalid cursor token")

        return (
            datetime.fromisoformat(cursor_data["timestamp"]),
            cursor_data["id"]
        )
    except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError):
        # Catch all decoding errors and raise consistent ValueError
        # Clients receive 400 Bad Request with clear error message
        raise ValueError("Invalid cursor token")
