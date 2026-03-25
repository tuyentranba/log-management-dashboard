"""
Analytics aggregation endpoints.

Provides GET /api/analytics with required date range filter,
optional severity/source filters, and aggregated log metrics.
"""
from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..dependencies import get_db
from ..models import Log
from ..schemas.analytics import (
    AnalyticsResponse,
    TimeSeriesDataPoint,
    SeverityDistributionPoint,
    SummaryStats
)

router = APIRouter()


def determine_granularity(date_from: datetime, date_to: datetime) -> str:
    """
    Determine optimal time bucket granularity based on date range.

    Returns PostgreSQL date_trunc unit optimized for chart readability:
    - Hourly buckets for ranges <3 days (max 72 points)
    - Daily buckets for 3-30 days (max 30 points)
    - Weekly buckets for >30 days (reduces long ranges)

    Args:
        date_from: Start of date range
        date_to: End of date range

    Returns:
        'hour', 'day', or 'week' for date_trunc() function
    """
    delta = date_to - date_from
    if delta < timedelta(days=3):
        return 'hour'
    elif delta <= timedelta(days=30):
        return 'day'
    else:
        return 'week'


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    # Required date range parameters (enforces ANALYTICS-06)
    date_from: Annotated[Optional[datetime], Query()] = None,
    date_to: Annotated[Optional[datetime], Query()] = None,
    # Optional filter parameters
    severity: Annotated[Optional[list[str]], Query()] = None,
    source: Annotated[Optional[str], Query()] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get analytics data with aggregations for dashboard visualization.

    Required parameters (enforces no unbounded COUNT queries):
        date_from: Start of date range (ISO 8601 with timezone)
        date_to: End of date range (ISO 8601 with timezone)

    Optional parameters:
        severity: Filter by one or more severity levels (INFO, WARNING, ERROR, CRITICAL)
        source: Filter by source (case-insensitive partial match)

    Returns:
        AnalyticsResponse with:
        - summary: Total count and breakdown by severity
        - time_series: Time-bucketed log counts with auto-adjusted granularity
        - severity_distribution: Count per severity level
        - granularity: Time bucket size used ('hour', 'day', or 'week')

    Raises:
        400: Date range missing or invalid (date_from > date_to)
    """
    # Enforce date range requirement (ANALYTICS-06: no unbounded COUNT queries)
    if not date_from or not date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range is required. Provide both date_from and date_to parameters."
        )

    # Validate date range is sensible
    if date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be before date_to"
        )

    # Build base WHERE clause for all queries (consistent filtering)
    base_filters = [
        Log.timestamp >= date_from,
        Log.timestamp <= date_to
    ]
    if severity:
        base_filters.append(Log.severity.in_(severity))
    if source:
        base_filters.append(Log.source.ilike(f"%{source}%"))

    # Query 1: Summary statistics with conditional aggregation
    # Single query computes total + per-severity counts efficiently
    summary_query = select(
        func.count().label('total'),
        func.count().filter(Log.severity == 'INFO').label('info_count'),
        func.count().filter(Log.severity == 'WARNING').label('warning_count'),
        func.count().filter(Log.severity == 'ERROR').label('error_count'),
        func.count().filter(Log.severity == 'CRITICAL').label('critical_count')
    ).where(*base_filters)

    summary_result = await db.execute(summary_query)
    summary_row = summary_result.one()

    # Query 2: Time-series data with auto-adjusted granularity
    # Uses PostgreSQL date_trunc() for efficient time bucketing
    granularity = determine_granularity(date_from, date_to)
    time_series_query = select(
        func.date_trunc(granularity, Log.timestamp).label('bucket'),
        func.count().label('count')
    ).where(
        *base_filters
    ).group_by('bucket').order_by('bucket')

    time_series_result = await db.execute(time_series_query)
    time_series_data = [
        TimeSeriesDataPoint(timestamp=row.bucket, count=row.count)
        for row in time_series_result
    ]

    # Query 3: Severity distribution with GROUP BY
    # Shows count per severity level for histogram
    severity_query = select(
        Log.severity,
        func.count().label('count')
    ).where(
        *base_filters
    ).group_by(Log.severity)

    severity_result = await db.execute(severity_query)
    severity_distribution = [
        SeverityDistributionPoint(severity=row.severity, count=row.count)
        for row in severity_result
    ]

    # Construct response with all aggregations
    return AnalyticsResponse(
        summary=SummaryStats(
            total=summary_row.total,
            by_severity={
                "INFO": summary_row.info_count,
                "WARNING": summary_row.warning_count,
                "ERROR": summary_row.error_count,
                "CRITICAL": summary_row.critical_count
            }
        ),
        time_series=time_series_data,
        severity_distribution=severity_distribution,
        granularity=granularity
    )
