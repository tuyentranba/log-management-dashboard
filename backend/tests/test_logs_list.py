"""
Integration tests for GET /api/logs list endpoint.

Tests cursor-based pagination, filtering, and sorting functionality.
"""
import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy import select
from app.models import Log


@pytest.mark.asyncio
async def test_list_logs_empty(client: AsyncClient, test_db):
    """GET /api/logs with empty database returns empty list."""
    response = await client.get("/api/logs")

    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["next_cursor"] is None
    assert data["has_more"] is False


@pytest.mark.asyncio
async def test_list_logs_default_limit(client: AsyncClient, test_db):
    """GET /api/logs returns 50 logs by default when more exist."""
    # Create 100 logs
    for i in range(100):
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=i),
            message=f"Test log {i}",
            severity="INFO",
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Fetch first page
    response = await client.get("/api/logs")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 50
    assert data["has_more"] is True
    assert data["next_cursor"] is not None


@pytest.mark.asyncio
async def test_list_logs_custom_limit(client: AsyncClient, test_db):
    """GET /api/logs?limit=25 returns exactly 25 logs."""
    # Create 100 logs
    for i in range(100):
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=i),
            message=f"Test log {i}",
            severity="INFO",
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Fetch with custom limit
    response = await client.get("/api/logs?limit=25")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 25
    assert data["has_more"] is True


@pytest.mark.asyncio
async def test_list_logs_max_limit(client: AsyncClient, test_db):
    """GET /api/logs?limit=300 returns 400 (exceeds max 200)."""
    response = await client.get("/api/logs?limit=300")

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_list_logs_has_more_true(client: AsyncClient, test_db):
    """GET /api/logs with more logs than limit sets has_more=true."""
    # Create 60 logs
    for i in range(60):
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=i),
            message=f"Test log {i}",
            severity="INFO",
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Fetch with limit 50
    response = await client.get("/api/logs?limit=50")

    assert response.status_code == 200
    data = response.json()
    assert data["has_more"] is True
    assert data["next_cursor"] is not None


@pytest.mark.asyncio
async def test_list_logs_has_more_false(client: AsyncClient, test_db):
    """GET /api/logs with fewer logs than limit sets has_more=false."""
    # Create 30 logs
    for i in range(30):
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=i),
            message=f"Test log {i}",
            severity="INFO",
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Fetch with limit 50
    response = await client.get("/api/logs?limit=50")

    assert response.status_code == 200
    data = response.json()
    assert data["has_more"] is False
    assert data["next_cursor"] is None


@pytest.mark.asyncio
async def test_list_logs_pagination_no_duplicates(client: AsyncClient, test_db):
    """Pagination returns no duplicate logs across pages."""
    # Create 100 logs
    for i in range(100):
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=i),
            message=f"Test log {i}",
            severity="INFO",
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Fetch page 1
    response1 = await client.get("/api/logs?limit=50")
    page1_ids = {log["id"] for log in response1.json()["data"]}

    # Fetch page 2 with cursor
    cursor = response1.json()["next_cursor"]
    response2 = await client.get(f"/api/logs?limit=50&cursor={cursor}")
    page2_ids = {log["id"] for log in response2.json()["data"]}

    # Verify no overlap
    assert len(page1_ids & page2_ids) == 0


@pytest.mark.asyncio
async def test_list_logs_pagination_complete(client: AsyncClient, test_db):
    """Pagination retrieves all logs without gaps."""
    # Create 100 logs
    for i in range(100):
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=i),
            message=f"Test log {i}",
            severity="INFO",
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Paginate through all logs
    all_ids = []
    cursor = None

    while True:
        url = f"/api/logs?limit=50&cursor={cursor}" if cursor else "/api/logs?limit=50"
        response = await client.get(url)

        assert response.status_code == 200
        data = response.json()
        all_ids.extend([log["id"] for log in data["data"]])

        if not data["has_more"]:
            break

        cursor = data["next_cursor"]

    # Verify exactly 100 unique logs
    assert len(all_ids) == 100
    assert len(set(all_ids)) == 100


@pytest.mark.asyncio
async def test_list_logs_invalid_cursor(client: AsyncClient, test_db):
    """GET /api/logs with invalid cursor returns 400."""
    response = await client.get("/api/logs?cursor=invalid-base64")

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid cursor" in data["detail"]


@pytest.mark.asyncio
async def test_list_logs_timestamp_order(client: AsyncClient, test_db):
    """GET /api/logs returns logs ordered by timestamp DESC (newest first)."""
    # Create logs with different timestamps
    timestamps = [
        datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc),
        datetime(2024, 3, 20, 11, 0, 0, tzinfo=timezone.utc),
        datetime(2024, 3, 20, 9, 0, 0, tzinfo=timezone.utc),
    ]

    for ts in timestamps:
        log = Log(
            timestamp=ts,
            message=f"Log at {ts.isoformat()}",
            severity="INFO",
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Fetch logs
    response = await client.get("/api/logs")

    assert response.status_code == 200
    data = response.json()["data"]

    # Verify descending order (newest first)
    assert len(data) == 3
    assert datetime.fromisoformat(data[0]["timestamp"]) > datetime.fromisoformat(data[1]["timestamp"])
    assert datetime.fromisoformat(data[1]["timestamp"]) > datetime.fromisoformat(data[2]["timestamp"])


# =====================================================================
# FILTERING TESTS
# =====================================================================


@pytest.mark.asyncio
async def test_filter_by_severity_single(client: AsyncClient, test_db):
    """GET /api/logs?severity=ERROR returns only ERROR logs."""
    # Create logs with different severities
    for severity in ["ERROR", "INFO"]:
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc),
            message=f"{severity} log",
            severity=severity,
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Filter for ERROR only
    response = await client.get("/api/logs?severity=ERROR")

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["severity"] == "ERROR"


@pytest.mark.asyncio
async def test_filter_by_severity_multiple(client: AsyncClient, test_db):
    """GET /api/logs with multiple severity filters returns matching logs."""
    # Create logs with different severities
    for severity in ["ERROR", "WARNING", "INFO", "CRITICAL"]:
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc),
            message=f"{severity} log",
            severity=severity,
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Filter for ERROR and WARNING
    response = await client.get("/api/logs?severity=ERROR&severity=WARNING")

    assert response.status_code == 200
    data = response.json()["data"]
    returned_severities = {log["severity"] for log in data}
    assert returned_severities == {"ERROR", "WARNING"}
    assert len(data) == 2


@pytest.mark.asyncio
async def test_filter_by_severity_invalid(client: AsyncClient, test_db):
    """GET /api/logs?severity=INVALID returns 400."""
    response = await client.get("/api/logs?severity=INVALID")

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid severity" in data["detail"]


@pytest.mark.asyncio
async def test_filter_by_source_exact(client: AsyncClient, test_db):
    """GET /api/logs?source=api returns logs with 'api' in source."""
    # Create logs with different sources
    for source in ["api-service", "auth-service"]:
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc),
            message=f"Log from {source}",
            severity="INFO",
            source=source
        )
        test_db.add(log)
    await test_db.commit()

    # Filter for 'api' (should match 'api-service')
    response = await client.get("/api/logs?source=api")

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert "api" in data[0]["source"].lower()


@pytest.mark.asyncio
async def test_filter_by_source_case_insensitive(client: AsyncClient, test_db):
    """GET /api/logs?source=api-service returns logs with case-insensitive match."""
    # Create log with source "API-Service"
    log = Log(
        timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc),
        message="Log from API-Service",
        severity="INFO",
        source="API-Service"
    )
    test_db.add(log)
    await test_db.commit()

    # Filter for lowercase 'api-service'
    response = await client.get("/api/logs?source=api-service")

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["source"] == "API-Service"


@pytest.mark.asyncio
async def test_filter_by_date_from(client: AsyncClient, test_db):
    """GET /api/logs?date_from=X returns logs on or after date_from."""
    # Create logs with different timestamps
    timestamps = [
        datetime(2024, 3, 19, 10, 0, 0, tzinfo=timezone.utc),
        datetime(2024, 3, 21, 10, 0, 0, tzinfo=timezone.utc),
    ]

    for ts in timestamps:
        log = Log(
            timestamp=ts,
            message=f"Log at {ts.isoformat()}",
            severity="INFO",
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Filter for logs on or after 2024-03-20
    response = await client.get("/api/logs?date_from=2024-03-20T00:00:00Z")

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert datetime.fromisoformat(data[0]["timestamp"]) >= datetime(2024, 3, 20, 0, 0, 0, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_filter_by_date_to(client: AsyncClient, test_db):
    """GET /api/logs?date_to=X returns logs on or before date_to."""
    # Create logs with different timestamps
    timestamps = [
        datetime(2024, 3, 19, 10, 0, 0, tzinfo=timezone.utc),
        datetime(2024, 3, 21, 10, 0, 0, tzinfo=timezone.utc),
    ]

    for ts in timestamps:
        log = Log(
            timestamp=ts,
            message=f"Log at {ts.isoformat()}",
            severity="INFO",
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Filter for logs on or before 2024-03-20
    response = await client.get("/api/logs?date_to=2024-03-20T00:00:00Z")

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert datetime.fromisoformat(data[0]["timestamp"]) <= datetime(2024, 3, 20, 0, 0, 0, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_filter_by_date_range(client: AsyncClient, test_db):
    """GET /api/logs?date_from=X&date_to=Y returns logs in range."""
    # Create logs across multiple days
    for day in [18, 19, 20, 21, 22]:
        log = Log(
            timestamp=datetime(2024, 3, day, 10, 0, 0, tzinfo=timezone.utc),
            message=f"Log on day {day}",
            severity="INFO",
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Filter for logs in range 2024-03-19 to 2024-03-21
    response = await client.get("/api/logs?date_from=2024-03-19T00:00:00Z&date_to=2024-03-21T23:59:59Z")

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 3  # Days 19, 20, 21


@pytest.mark.asyncio
async def test_filter_combined(client: AsyncClient, test_db):
    """GET /api/logs with multiple filters returns intersection."""
    # Create diverse logs
    logs_data = [
        {"timestamp": datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc), "severity": "ERROR", "source": "api-service"},
        {"timestamp": datetime(2024, 3, 20, 11, 0, 0, tzinfo=timezone.utc), "severity": "ERROR", "source": "auth-service"},
        {"timestamp": datetime(2024, 3, 21, 10, 0, 0, tzinfo=timezone.utc), "severity": "ERROR", "source": "api-service"},
        {"timestamp": datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc), "severity": "INFO", "source": "api-service"},
    ]

    for log_data in logs_data:
        log = Log(
            timestamp=log_data["timestamp"],
            message="Test log",
            severity=log_data["severity"],
            source=log_data["source"]
        )
        test_db.add(log)
    await test_db.commit()

    # Filter: ERROR logs from api-service on 2024-03-20
    response = await client.get("/api/logs?severity=ERROR&source=api&date_from=2024-03-20T00:00:00Z&date_to=2024-03-20T23:59:59Z")

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1  # Only first log matches all filters
    assert data[0]["severity"] == "ERROR"
    assert "api" in data[0]["source"].lower()


# =====================================================================
# SORTING TESTS
# =====================================================================


@pytest.mark.asyncio
async def test_sort_by_severity_asc(client: AsyncClient, test_db):
    """GET /api/logs?sort=severity&order=asc returns logs ordered by severity."""
    # Create logs with different severities
    for severity in ["ERROR", "INFO", "WARNING", "CRITICAL"]:
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc),
            message=f"{severity} log",
            severity=severity,
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Sort by severity ascending
    response = await client.get("/api/logs?sort=severity&order=asc")

    assert response.status_code == 200
    data = response.json()["data"]
    severities = [log["severity"] for log in data]
    assert severities == ["CRITICAL", "ERROR", "INFO", "WARNING"]


@pytest.mark.asyncio
async def test_sort_by_severity_desc(client: AsyncClient, test_db):
    """GET /api/logs?sort=severity&order=desc returns logs in reverse order."""
    # Create logs with different severities
    for severity in ["ERROR", "INFO", "WARNING"]:
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc),
            message=f"{severity} log",
            severity=severity,
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Sort by severity descending
    response = await client.get("/api/logs?sort=severity&order=desc")

    assert response.status_code == 200
    data = response.json()["data"]
    severities = [log["severity"] for log in data]
    assert severities == ["WARNING", "INFO", "ERROR"]


@pytest.mark.asyncio
async def test_sort_by_source(client: AsyncClient, test_db):
    """GET /api/logs?sort=source&order=asc returns logs ordered by source."""
    # Create logs with different sources
    for source in ["zoo-service", "api-service", "middle-service"]:
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc),
            message=f"Log from {source}",
            severity="INFO",
            source=source
        )
        test_db.add(log)
    await test_db.commit()

    # Sort by source ascending
    response = await client.get("/api/logs?sort=source&order=asc")

    assert response.status_code == 200
    data = response.json()["data"]
    sources = [log["source"] for log in data]
    assert sources == ["api-service", "middle-service", "zoo-service"]


@pytest.mark.asyncio
async def test_sort_invalid_field(client: AsyncClient, test_db):
    """GET /api/logs?sort=invalid_field returns 400."""
    response = await client.get("/api/logs?sort=invalid_field")

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_sort_invalid_order(client: AsyncClient, test_db):
    """GET /api/logs?sort=timestamp&order=invalid returns 400."""
    response = await client.get("/api/logs?sort=timestamp&order=invalid")

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_pagination_with_filters(client: AsyncClient, test_db):
    """Pagination works correctly with filters applied."""
    # Create 100 logs (50 ERROR, 50 INFO)
    for i in range(100):
        log = Log(
            timestamp=datetime(2024, 3, 20, 10, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=i),
            message=f"Test log {i}",
            severity="ERROR" if i % 2 == 0 else "INFO",
            source="test"
        )
        test_db.add(log)
    await test_db.commit()

    # Filter for ERROR logs with limit 25
    response = await client.get("/api/logs?severity=ERROR&limit=25")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 25
    assert all(log["severity"] == "ERROR" for log in data["data"])
    assert data["has_more"] is True
