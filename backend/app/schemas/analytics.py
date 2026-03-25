"""
Pydantic schemas for analytics API endpoints.

Provides request/response validation for aggregated log metrics
with time-series and severity distribution data.
"""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class TimeSeriesDataPoint(BaseModel):
    """
    Single data point in time-series chart.

    Represents aggregated log count for a specific time bucket
    (hour/day/week depending on date range).
    """
    timestamp: datetime
    count: int


class SeverityDistributionPoint(BaseModel):
    """
    Single data point in severity distribution chart.

    Represents total log count for a specific severity level.
    """
    severity: Literal['INFO', 'WARNING', 'ERROR', 'CRITICAL']
    count: int


class SummaryStats(BaseModel):
    """
    Summary statistics for filtered log set.

    Includes total count and breakdown by severity level.
    """
    total: int
    by_severity: dict[str, int]  # {"INFO": 1234, "WARNING": 567, ...}


class AnalyticsResponse(BaseModel):
    """
    Complete analytics response with all aggregations.

    Compatible with SQLAlchemy aggregation queries via from_attributes.
    """
    summary: SummaryStats
    time_series: list[TimeSeriesDataPoint]
    severity_distribution: list[SeverityDistributionPoint]
    granularity: Literal['hour', 'day', 'week']

    model_config = {"from_attributes": True}  # Enable ORM mode for SQLAlchemy
