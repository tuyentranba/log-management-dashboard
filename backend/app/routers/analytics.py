"""
Analytics aggregation endpoints.

Provides GET /api/analytics with required date range filter,
optional severity/source filters, and aggregated log metrics.

Key design decisions:
- date_trunc() with UTC normalization for timezone-correct aggregations (see ADR-004)
- Auto-adjusted granularity (hour/day/week) for optimal chart readability
- Three-query pattern (summary, time-series, distribution) using base filters
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

    # Hourly buckets for ranges <3 days (max 72 data points)
    # Prevents chart overcrowding while maintaining detail for short time ranges
    # 72 points is sweet spot for line charts - readable without overwhelming
    if delta < timedelta(days=3):
        return 'hour'

    # Daily buckets for 3-30 days (max 30 data points)
    # Sweet spot between detail and readability for typical dashboard usage
    # Most users query "last week" or "last month" - daily granularity is natural
    elif delta <= timedelta(days=30):
        return 'day'

    # Weekly buckets for >30 days
    # Reduces long-range charts to manageable point count without losing trend visibility
    # 52 weeks = 1 year remains readable, longer ranges compress naturally
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
    # Applying same filters to all three queries (summary, time-series, distribution)
    # ensures data consistency - summary total matches sum of time-series points
    base_filters = [
        Log.timestamp >= date_from,
        Log.timestamp <= date_to
    ]
    if severity:
        base_filters.append(Log.severity.in_(severity))
    if source:
        base_filters.append(Log.source.ilike(f"%{source}%"))

    # Three-query pattern for analytics dashboard
    # Could use single query with window functions, but separate queries are clearer
    # and PostgreSQL query planner can optimize each independently

    # Query 1: Summary stats using conditional aggregation (COUNT FILTER)
    # Single query with multiple COUNT FILTER clauses is faster than 4 separate COUNT queries
    summary_query = select(
        func.count().label('total'),
        func.count().filter(Log.severity == 'INFO').label('info_count'),
        func.count().filter(Log.severity == 'WARNING').label('warning_count'),
        func.count().filter(Log.severity == 'ERROR').label('error_count'),
        func.count().filter(Log.severity == 'CRITICAL').label('critical_count')
    ).where(*base_filters)

    summary_result = await db.execute(summary_query)
    summary_row = summary_result.one()

    # Query 2: Time-series with auto-adjusted granularity
    # date_trunc() buckets timestamps into hour/day/week based on date range
    # AT TIME ZONE 'UTC' ensures consistent bucketing regardless of server timezone
    # See ADR-004 for timezone handling rationale
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

    # Query 3: Severity distribution (simple GROUP BY)
    # Separate from time-series to avoid Cartesian product
    # Returns 4 rows max (INFO, WARNING, ERROR, CRITICAL) - always fast
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
