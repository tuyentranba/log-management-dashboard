"""
Cursor encoding/decoding utilities for pagination.

Provides opaque cursor tokens for cursor-based pagination,
allowing internal implementation changes without breaking clients.
"""
import base64
import json
from datetime import datetime
from typing import Tuple


def encode_cursor(timestamp: datetime, log_id: int) -> str:
    """
    Encode pagination cursor as opaque base64 string.

    Args:
        timestamp: Log timestamp (must be timezone-aware)
        log_id: Log primary key

    Returns:
        Base64-encoded JSON string containing timestamp (ISO format) and id

    Example:
        encode_cursor(datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc), 123)
        # Returns: "eyJ0aW1lc3RhbXAiOiAiMjAyNC0wMy0yMFQxNTozMDowMCswMDowMCIsICJpZCI6IDEyM30="
    """
    cursor_data = {
        "timestamp": timestamp.isoformat(),
        "id": log_id
    }
    json_str = json.dumps(cursor_data)
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

        # Validate required fields exist
        if "timestamp" not in cursor_data or "id" not in cursor_data:
            raise ValueError("Invalid cursor token")

        return (
            datetime.fromisoformat(cursor_data["timestamp"]),
            cursor_data["id"]
        )
    except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Invalid cursor token")
