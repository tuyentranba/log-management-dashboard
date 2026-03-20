"""
Pydantic schemas for log API endpoints.

Provides request/response validation with timezone enforcement
and severity enum validation.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class LogCreate(BaseModel):
    """
    Request schema for creating logs.

    Enforces timezone-aware timestamps and validates severity enum.
    """
    timestamp: datetime = Field(
        description="Log timestamp in ISO 8601 format with timezone (e.g., 2024-03-20T15:30:00Z)"
    )
    message: str = Field(
        min_length=1,
        description="Log message content"
    )
    severity: str = Field(
        pattern="^(INFO|WARNING|ERROR|CRITICAL)$",
        description="Log severity level: INFO, WARNING, ERROR, or CRITICAL"
    )
    source: str = Field(
        min_length=1,
        max_length=100,
        description="Log source identifier (e.g., service name)"
    )

    @field_validator('timestamp')
    @classmethod
    def validate_timezone_aware(cls, v: datetime) -> datetime:
        """
        Ensure timestamp includes timezone information.

        Raises:
            ValueError: If timestamp is timezone-naive
        """
        if v.tzinfo is None:
            raise ValueError(
                "Timestamp must include timezone. "
                "Use ISO 8601 format: 2024-03-20T15:30:00Z"
            )
        return v


class LogResponse(BaseModel):
    """
    Response schema for log objects.

    Compatible with SQLAlchemy Log model via from_attributes.
    """
    id: int
    timestamp: datetime
    message: str
    severity: str
    source: str

    model_config = {"from_attributes": True}  # Enable ORM mode for SQLAlchemy


class LogListResponse(BaseModel):
    """
    Response envelope for paginated log list.

    Includes data array, pagination cursor, and has_more flag.
    """
    data: list[LogResponse] = Field(
        description="Array of log objects for current page"
    )
    next_cursor: Optional[str] = Field(
        default=None,
        description="Opaque cursor token for next page, null if no more pages"
    )
    has_more: bool = Field(
        description="True if more pages exist, false otherwise"
    )
