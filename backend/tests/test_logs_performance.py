"""
Performance tests for cursor-based pagination at scale.

These tests validate that pagination performance remains constant
with large datasets (100k+ logs), avoiding OFFSET degradation.
"""
import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy import select
from app.models import Log
import time
from urllib.parse import quote

pytestmark = pytest.mark.slow  # Mark all tests in this file as slow


@pytest.mark.asyncio
async def test_pagination_performance_first_page(client: AsyncClient, test_db):
    """First page loads quickly even with 100k logs."""
    # Create 100k logs (use efficient bulk insert like seed script)
    logs = []
    base_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    for i in range(100_000):
        logs.append({
            "timestamp": base_time + timedelta(seconds=i * 25),
            "message": f"Performance test log {i}",
            "severity": "INFO" if i % 2 == 0 else "ERROR",
            "source": f"service-{i % 5}"
        })

    # Bulk insert for speed using test_db session
    await test_db.run_sync(
        lambda sync_session: sync_session.bulk_insert_mappings(Log, logs)
    )
    await test_db.commit()

    # Measure first page query time
    start = time.perf_counter()
    response = await client.get("/api/logs?limit=50")
    duration_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert len(response.json()["data"]) == 50
    # First page should be very fast (well under 500ms target)
    assert duration_ms < 500, f"First page took {duration_ms:.2f}ms (target: <500ms)"


@pytest.mark.asyncio
async def test_pagination_performance_deep_page(client: AsyncClient, test_db):
    """Page 100+ loads quickly with cursor pagination (no OFFSET degradation)."""
    # Create 100k logs (same as above)
    logs = []
    base_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    for i in range(100_000):
        logs.append({
            "timestamp": base_time + timedelta(seconds=i * 25),
            "message": f"Performance test log {i}",
            "severity": "INFO" if i % 2 == 0 else "ERROR",
            "source": f"service-{i % 5}"
        })

    # Bulk insert for speed using test_db session
    await test_db.run_sync(
        lambda sync_session: sync_session.bulk_insert_mappings(Log, logs)
    )
    await test_db.commit()

    # Navigate to page 100 (5000 logs in)
    cursor = None
    for page in range(100):
        response = await client.get(f"/api/logs?limit=50&cursor={cursor}" if cursor else "/api/logs?limit=50")
        assert response.status_code == 200
        cursor = response.json()["next_cursor"]
        if not cursor:
            pytest.fail(f"Ran out of pages at page {page + 1}, expected to reach page 100")

    # Measure page 100 query time
    start = time.perf_counter()
    response = await client.get(f"/api/logs?limit=50&cursor={cursor}")
    duration_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert len(response.json()["data"]) == 50
    # Deep page should have similar performance to first page (no OFFSET degradation)
    assert duration_ms < 500, f"Page 100 took {duration_ms:.2f}ms (target: <500ms)"
    print(f"Page 100 performance: {duration_ms:.2f}ms")


@pytest.mark.asyncio
async def test_pagination_consistency_with_scale(client: AsyncClient, test_db):
    """Pagination returns consistent boundaries with 100k logs (no duplicates or gaps)."""
    # Create 10k logs (smaller dataset for faster test, still validates consistency)
    logs = []
    base_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    for i in range(10_000):
        logs.append({
            "timestamp": base_time + timedelta(seconds=i),
            "message": f"Test log {i}",
            "severity": "INFO",
            "source": "test"
        })

    # Bulk insert for speed using test_db session
    await test_db.run_sync(
        lambda sync_session: sync_session.bulk_insert_mappings(Log, logs)
    )
    await test_db.commit()

    # Paginate through all logs
    all_ids = []
    cursor = None
    page_count = 0

    while True:
        response = await client.get(f"/api/logs?limit=100&cursor={cursor}" if cursor else "/api/logs?limit=100")
        assert response.status_code == 200

        data = response.json()
        page_ids = [log["id"] for log in data["data"]]
        all_ids.extend(page_ids)

        page_count += 1
        if not data["has_more"]:
            break

        cursor = data["next_cursor"]
        if page_count > 150:  # Safety check
            pytest.fail("Infinite pagination loop detected")

    # Verify no duplicates (set conversion would remove duplicates)
    assert len(all_ids) == len(set(all_ids)), "Duplicate log IDs found across pages"
    # Verify all logs retrieved
    assert len(all_ids) == 10_000, f"Expected 10000 logs, got {len(all_ids)}"


@pytest.mark.asyncio
async def test_analytics_query_performance_with_100k_logs(client: AsyncClient, test_db):
    """Analytics queries complete quickly (<2s) even with 100k logs."""
    # Create 100k logs with varied timestamps spread over 41 days
    logs = []
    base_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    severities = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']

    for i in range(100_000):
        logs.append({
            "timestamp": base_time + timedelta(hours=i // 100),
            "message": f"Log message {i}",
            "severity": severities[i % 4],
            "source": f"service-{i % 5}"
        })

    # Bulk insert for speed
    await test_db.run_sync(
        lambda sync_session: sync_session.bulk_insert_mappings(Log, logs)
    )
    await test_db.commit()

    # Measure analytics query time with 30-day date range
    date_from = quote(base_time.isoformat())
    date_to = quote((base_time + timedelta(days=30)).isoformat())

    start = time.perf_counter()
    response = await client.get(f"/api/analytics?date_from={date_from}&date_to={date_to}")
    duration_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "time_series" in data
    assert "severity_distribution" in data
    assert duration_ms < 2000, f"Analytics query took {duration_ms:.2f}ms (target: <2000ms)"


@pytest.mark.asyncio
async def test_csv_export_performance_with_large_filtered_dataset(client: AsyncClient, test_db):
    """CSV export with filters completes quickly (<3s) even with 100k logs."""
    # Create 100k logs with varied timestamps
    logs = []
    base_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    severities = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']

    for i in range(100_000):
        logs.append({
            "timestamp": base_time + timedelta(hours=i // 100),
            "message": f"Log message {i}",
            "severity": severities[i % 4],
            "source": f"service-{i % 5}"
        })

    # Bulk insert for speed
    await test_db.run_sync(
        lambda sync_session: sync_session.bulk_insert_mappings(Log, logs)
    )
    await test_db.commit()

    # Measure CSV export time with multi-filter query
    start = time.perf_counter()
    response = await client.get("/api/export?severity=ERROR&severity=CRITICAL&source=service-1")
    duration_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
    assert duration_ms < 3000, f"CSV export took {duration_ms:.2f}ms (target: <3000ms)"

    # Verify CSV contains UTF-8 BOM and proper headers
    csv_content = response.text
    assert csv_content.startswith('\ufeff')  # UTF-8 BOM
    assert 'Timestamp,Severity,Source,Message' in csv_content


@pytest.mark.asyncio
async def test_pagination_with_multi_filter_combination(client: AsyncClient, test_db):
    """Multi-filter pagination maintains performance (<500ms avg) across pages."""
    # Create 100k logs with mixed severities and sources
    logs = []
    base_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    severities = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']

    for i in range(100_000):
        logs.append({
            "timestamp": base_time + timedelta(hours=i // 100),
            "message": f"Log message {i}",
            "severity": severities[i % 4],
            "source": f"service-{i % 5}"
        })

    # Bulk insert for speed
    await test_db.run_sync(
        lambda sync_session: sync_session.bulk_insert_mappings(Log, logs)
    )
    await test_db.commit()

    # Apply date range + severity + source filters simultaneously
    date_from = quote(base_time.isoformat())
    date_to = quote((base_time + timedelta(days=30)).isoformat())
    filter_params = f"date_from={date_from}&date_to={date_to}&severity=ERROR&severity=WARNING&source=service-2"

    # Paginate through first 5 pages (50 logs each)
    cursor = None
    durations = []
    all_ids = set()

    for page in range(5):
        url = f"/api/logs?{filter_params}&limit=50"
        if cursor:
            url += f"&cursor={cursor}"

        start = time.perf_counter()
        response = await client.get(url)
        duration_ms = (time.perf_counter() - start) * 1000
        durations.append(duration_ms)

        assert response.status_code == 200
        data = response.json()

        # Collect IDs to verify no duplicates
        page_ids = {log["id"] for log in data["data"]}
        assert not (page_ids & all_ids), "Duplicate logs found across pages"
        all_ids.update(page_ids)

        cursor = data.get("next_cursor")
        if not data["has_more"]:
            break

    # Calculate average page load time
    avg_duration_ms = sum(durations) / len(durations)
    assert avg_duration_ms < 500, f"Multi-filter pagination averaged {avg_duration_ms:.2f}ms (target: <500ms)"
    print(f"Multi-filter pagination: {len(durations)} pages averaged {avg_duration_ms:.2f}ms")
