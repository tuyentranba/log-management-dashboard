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
