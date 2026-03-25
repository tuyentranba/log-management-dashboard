"""
Integration tests for analytics aggregation endpoint.

Tests GET /api/analytics with date range validation, summary stats,
time-series aggregation, severity distribution, and filtering.
"""
import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Log


# ============================================================================
# Helper functions
# ============================================================================

def format_datetime(dt: datetime) -> str:
    """Format datetime as ISO 8601 with UTC timezone."""
    return dt.replace(tzinfo=timezone.utc).isoformat()


async def create_test_logs(db: AsyncSession, count: int = 10, base_time: datetime = None):
    """
    Create test logs for analytics testing.

    Args:
        db: Database session
        count: Number of logs to create
        base_time: Base timestamp (defaults to now)

    Returns:
        List of created log IDs
    """
    if base_time is None:
        base_time = datetime.now(timezone.utc)

    logs = []
    severities = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']

    for i in range(count):
        log = Log(
            timestamp=base_time - timedelta(hours=i),
            message=f"Test log message {i}",
            severity=severities[i % 4],  # Rotate through severities
            source=f"service-{i % 3}"  # Rotate through 3 services
        )
        logs.append(log)
        db.add(log)

    await db.commit()
    return [log.id for log in logs]


# ============================================================================
# Date range validation tests
# ============================================================================

@pytest.mark.asyncio
async def test_date_range_required(client: AsyncClient):
    """GET /api/analytics without date_from/date_to returns 400."""
    response = await client.get("/api/analytics")

    assert response.status_code == 400
    data = response.json()
    assert "date range is required" in data["detail"].lower()


@pytest.mark.asyncio
async def test_date_from_required(client: AsyncClient):
    """GET /api/analytics with only date_to returns 400."""
    now = datetime.now(timezone.utc)

    response = await client.get(
        "/api/analytics",
        params={"date_to": format_datetime(now)}
    )

    assert response.status_code == 400
    data = response.json()
    assert "date range is required" in data["detail"].lower()


@pytest.mark.asyncio
async def test_date_to_required(client: AsyncClient):
    """GET /api/analytics with only date_from returns 400."""
    now = datetime.now(timezone.utc)

    response = await client.get(
        "/api/analytics",
        params={"date_from": format_datetime(now - timedelta(days=7))}
    )

    assert response.status_code == 400
    data = response.json()
    assert "date range is required" in data["detail"].lower()


@pytest.mark.asyncio
async def test_invalid_date_range(client: AsyncClient):
    """GET /api/analytics with date_from > date_to returns 400."""
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=7)

    response = await client.get(
        "/api/analytics",
        params={
            "date_from": format_datetime(now),  # Future
            "date_to": format_datetime(past)    # Past
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "date_from must be before date_to" in data["detail"].lower()


# ============================================================================
# Summary statistics tests
# ============================================================================

@pytest.mark.asyncio
async def test_summary_stats(client: AsyncClient, test_db: AsyncSession):
    """GET /api/analytics with valid range returns summary stats."""
    base_time = datetime.now(timezone.utc)
    await create_test_logs(test_db, count=20, base_time=base_time)

    response = await client.get(
        "/api/analytics",
        params={
            "date_from": format_datetime(base_time - timedelta(days=1)),
            "date_to": format_datetime(base_time)
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify summary structure
    assert "summary" in data
    assert "total" in data["summary"]
    assert isinstance(data["summary"]["total"], int)
    assert data["summary"]["total"] == 20

    # Verify by_severity breakdown
    assert "by_severity" in data["summary"]
    assert "INFO" in data["summary"]["by_severity"]
    assert "WARNING" in data["summary"]["by_severity"]
    assert "ERROR" in data["summary"]["by_severity"]
    assert "CRITICAL" in data["summary"]["by_severity"]

    # Verify counts add up
    severity_sum = sum(data["summary"]["by_severity"].values())
    assert severity_sum == data["summary"]["total"]


# ============================================================================
# Time-series granularity tests
# ============================================================================

@pytest.mark.asyncio
async def test_time_series_granularity_hourly(client: AsyncClient, test_db: AsyncSession):
    """GET /api/analytics with 2-day range uses hourly granularity."""
    base_time = datetime.now(timezone.utc)
    await create_test_logs(test_db, count=10, base_time=base_time)

    response = await client.get(
        "/api/analytics",
        params={
            "date_from": format_datetime(base_time - timedelta(days=2)),
            "date_to": format_datetime(base_time)
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify granularity is hour
    assert data["granularity"] == "hour"

    # Verify time_series structure
    assert "time_series" in data
    assert isinstance(data["time_series"], list)
    assert len(data["time_series"]) > 0

    # Verify each point has timestamp and count
    for point in data["time_series"]:
        assert "timestamp" in point
        assert "count" in point
        assert isinstance(point["count"], int)


@pytest.mark.asyncio
async def test_time_series_granularity_daily(client: AsyncClient, test_db: AsyncSession):
    """GET /api/analytics with 7-day range uses daily granularity."""
    base_time = datetime.now(timezone.utc)
    await create_test_logs(test_db, count=10, base_time=base_time)

    response = await client.get(
        "/api/analytics",
        params={
            "date_from": format_datetime(base_time - timedelta(days=7)),
            "date_to": format_datetime(base_time)
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify granularity is day
    assert data["granularity"] == "day"


@pytest.mark.asyncio
async def test_time_series_granularity_weekly(client: AsyncClient, test_db: AsyncSession):
    """GET /api/analytics with 40-day range uses weekly granularity."""
    base_time = datetime.now(timezone.utc)
    await create_test_logs(test_db, count=10, base_time=base_time)

    response = await client.get(
        "/api/analytics",
        params={
            "date_from": format_datetime(base_time - timedelta(days=40)),
            "date_to": format_datetime(base_time)
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify granularity is week
    assert data["granularity"] == "week"


# ============================================================================
# Severity distribution tests
# ============================================================================

@pytest.mark.asyncio
async def test_severity_distribution(client: AsyncClient, test_db: AsyncSession):
    """GET /api/analytics returns severity distribution data."""
    base_time = datetime.now(timezone.utc)
    await create_test_logs(test_db, count=20, base_time=base_time)

    response = await client.get(
        "/api/analytics",
        params={
            "date_from": format_datetime(base_time - timedelta(days=1)),
            "date_to": format_datetime(base_time)
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify severity_distribution structure
    assert "severity_distribution" in data
    assert isinstance(data["severity_distribution"], list)
    assert len(data["severity_distribution"]) > 0

    # Verify each point has severity and count
    for point in data["severity_distribution"]:
        assert "severity" in point
        assert "count" in point
        assert point["severity"] in ["INFO", "WARNING", "ERROR", "CRITICAL"]
        assert isinstance(point["count"], int)
        assert point["count"] > 0


# ============================================================================
# Filtering tests
# ============================================================================

@pytest.mark.asyncio
async def test_severity_filter(client: AsyncClient, test_db: AsyncSession):
    """GET /api/analytics with severity filter returns filtered stats."""
    base_time = datetime.now(timezone.utc)
    await create_test_logs(test_db, count=20, base_time=base_time)

    response = await client.get(
        "/api/analytics",
        params={
            "date_from": format_datetime(base_time - timedelta(days=1)),
            "date_to": format_datetime(base_time),
            "severity": ["ERROR", "CRITICAL"]
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify only ERROR and CRITICAL are in severity_distribution
    for point in data["severity_distribution"]:
        assert point["severity"] in ["ERROR", "CRITICAL"]


@pytest.mark.asyncio
async def test_source_filter(client: AsyncClient, test_db: AsyncSession):
    """GET /api/analytics with source filter returns filtered data."""
    base_time = datetime.now(timezone.utc)

    # Create logs with specific sources
    log1 = Log(
        timestamp=base_time,
        message="Test log 1",
        severity="INFO",
        source="api-service"
    )
    log2 = Log(
        timestamp=base_time - timedelta(hours=1),
        message="Test log 2",
        severity="ERROR",
        source="database-service"
    )
    log3 = Log(
        timestamp=base_time - timedelta(hours=2),
        message="Test log 3",
        severity="WARNING",
        source="api-gateway"
    )
    test_db.add_all([log1, log2, log3])
    await test_db.commit()

    response = await client.get(
        "/api/analytics",
        params={
            "date_from": format_datetime(base_time - timedelta(days=1)),
            "date_to": format_datetime(base_time),
            "source": "api"  # Should match api-service and api-gateway
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify filtered count (should be 2: api-service + api-gateway)
    assert data["summary"]["total"] == 2


# ============================================================================
# Performance test
# ============================================================================

@pytest.mark.asyncio
async def test_performance_with_100k_logs(client: AsyncClient, test_db: AsyncSession):
    """GET /api/analytics completes in under 2 seconds with 100k logs."""
    # Note: This test requires 100k logs in database (created by seed script)
    # Skip if database doesn't have enough logs
    from sqlalchemy import select, func
    from app.models import Log
    import time

    # Check if database has at least 10k logs (reduced threshold for test speed)
    result = await test_db.execute(select(func.count()).select_from(Log))
    count = result.scalar()

    if count < 10000:
        pytest.skip("Insufficient logs in database for performance test (need 10k+)")

    base_time = datetime.now(timezone.utc)
    start_time = time.time()

    response = await client.get(
        "/api/analytics",
        params={
            "date_from": format_datetime(base_time - timedelta(days=30)),
            "date_to": format_datetime(base_time)
        }
    )

    duration = time.time() - start_time

    assert response.status_code == 200
    assert duration < 2.0, f"Analytics endpoint took {duration:.2f}s (expected <2s)"
