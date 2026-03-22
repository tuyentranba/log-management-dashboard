"""
Integration tests for CSV export endpoint.

Tests all EXPORT-* requirements:
- EXPORT-01: User can export filtered log data as CSV
- EXPORT-02: CSV export uses streaming response
- EXPORT-03: CSV export includes all log fields
"""
import pytest
import csv
import io
from datetime import datetime, timezone, timedelta
from fastapi.responses import StreamingResponse
from app.models import Log


def parse_csv_response(response_content: bytes) -> list[list[str]]:
    """Parse CSV bytes into list of rows."""
    content = response_content.decode('utf-8-sig')  # Remove BOM
    reader = csv.reader(io.StringIO(content))
    return list(reader)


# EXPORT-01 tests (filtering)


@pytest.mark.asyncio
async def test_export_no_filters(client, test_db):
    """Export with no filters returns all logs in CSV format."""
    # Create 5 test logs
    now = datetime.now(timezone.utc)
    for i in range(5):
        log = Log(
            timestamp=now + timedelta(minutes=i),
            severity="INFO",
            source="test-service",
            message=f"Test message {i}"
        )
        test_db.add(log)
    await test_db.commit()

    # Export without filters
    response = await client.get("/api/export")
    assert response.status_code == 200

    # Parse CSV
    rows = parse_csv_response(response.content)
    assert len(rows) == 6  # header + 5 data rows
    assert rows[0] == ['Timestamp', 'Severity', 'Source', 'Message']


@pytest.mark.asyncio
async def test_export_severity_filter(client, test_db):
    """Export with severity filter returns only matching logs."""
    now = datetime.now(timezone.utc)
    # Create logs with mixed severities
    for i, severity in enumerate(['ERROR', 'INFO', 'ERROR', 'WARNING', 'ERROR']):
        log = Log(
            timestamp=now + timedelta(minutes=i),
            severity=severity,
            source="test-service",
            message=f"Test message {i}"
        )
        test_db.add(log)
    await test_db.commit()

    # Export with severity=ERROR
    response = await client.get("/api/export?severity=ERROR")
    assert response.status_code == 200

    # Parse CSV
    rows = parse_csv_response(response.content)
    assert len(rows) == 4  # header + 3 ERROR logs
    # Verify all data rows have ERROR severity
    for row in rows[1:]:
        assert row[1] == 'ERROR'


@pytest.mark.asyncio
async def test_export_source_filter(client, test_db):
    """Export with source filter returns only matching logs."""
    now = datetime.now(timezone.utc)
    # Create logs with different sources
    for i, source in enumerate(['api-service', 'auth-service', 'api-service', 'database']):
        log = Log(
            timestamp=now + timedelta(minutes=i),
            severity="INFO",
            source=source,
            message=f"Test message {i}"
        )
        test_db.add(log)
    await test_db.commit()

    # Export with source=api (case-insensitive partial match)
    response = await client.get("/api/export?source=api")
    assert response.status_code == 200

    # Parse CSV
    rows = parse_csv_response(response.content)
    assert len(rows) == 3  # header + 2 api-service logs
    # Verify all data rows have 'api' in source
    for row in rows[1:]:
        assert 'api' in row[2].lower()


@pytest.mark.asyncio
async def test_export_date_range_filter(client, test_db):
    """Export with date range filter returns only logs in range."""
    base_date = datetime(2025, 3, 20, 12, 0, 0, tzinfo=timezone.utc)
    # Create logs across 7 days
    for i in range(7):
        log = Log(
            timestamp=base_date + timedelta(days=i),
            severity="INFO",
            source="test-service",
            message=f"Day {i}"
        )
        test_db.add(log)
    await test_db.commit()

    # Export days 2-4 (inclusive) - use params dict for proper URL encoding
    date_from = (base_date + timedelta(days=2)).isoformat()
    date_to = (base_date + timedelta(days=4)).isoformat()
    response = await client.get("/api/export", params={"date_from": date_from, "date_to": date_to})
    assert response.status_code == 200

    # Parse CSV
    rows = parse_csv_response(response.content)
    assert len(rows) == 4  # header + 3 days (days 2, 3, 4)


@pytest.mark.asyncio
async def test_export_combined_filters(client, test_db):
    """Export with combined filters returns correct intersection."""
    base_date = datetime(2025, 3, 20, 12, 0, 0, tzinfo=timezone.utc)
    # Create diverse logs
    test_cases = [
        (base_date, 'ERROR', 'api-service', 'Match 1'),
        (base_date + timedelta(days=1), 'ERROR', 'api-service', 'Match 2'),
        (base_date + timedelta(days=2), 'INFO', 'api-service', 'No match - severity'),
        (base_date + timedelta(days=3), 'ERROR', 'auth-service', 'No match - source'),
        (base_date + timedelta(days=10), 'ERROR', 'api-service', 'No match - date'),
    ]
    for timestamp, severity, source, message in test_cases:
        log = Log(timestamp=timestamp, severity=severity, source=source, message=message)
        test_db.add(log)
    await test_db.commit()

    # Export with combined filters - use params dict for proper URL encoding
    date_from = base_date.isoformat()
    date_to = (base_date + timedelta(days=5)).isoformat()
    response = await client.get("/api/export", params={
        "severity": "ERROR",
        "source": "api",
        "date_from": date_from,
        "date_to": date_to
    })
    assert response.status_code == 200

    # Parse CSV
    rows = parse_csv_response(response.content)
    assert len(rows) == 3  # header + 2 matching logs
    # Verify correct logs matched (sorted by timestamp desc, so Match 2 comes first)
    assert 'Match 2' in rows[1][3]
    assert 'Match 1' in rows[2][3]


@pytest.mark.asyncio
async def test_export_sort_order(client, test_db):
    """Export respects sort parameter."""
    now = datetime.now(timezone.utc)
    # Create logs with different severities
    for i, severity in enumerate(['WARNING', 'CRITICAL', 'ERROR', 'INFO']):
        log = Log(
            timestamp=now + timedelta(minutes=i),
            severity=severity,
            source="test-service",
            message=f"Message {i}"
        )
        test_db.add(log)
    await test_db.commit()

    # Export with sort=severity&order=asc
    response = await client.get("/api/export?sort=severity&order=asc")
    assert response.status_code == 200

    # Parse CSV
    rows = parse_csv_response(response.content)
    severities = [row[1] for row in rows[1:]]  # Skip header
    # Verify alphabetical order (CRITICAL, ERROR, INFO, WARNING)
    assert severities == ['CRITICAL', 'ERROR', 'INFO', 'WARNING']


# EXPORT-02 tests (streaming)


@pytest.mark.asyncio
async def test_export_returns_streaming_response(client, test_db):
    """Export endpoint returns StreamingResponse type."""
    # Create one log
    log = Log(
        timestamp=datetime.now(timezone.utc),
        severity="INFO",
        source="test-service",
        message="Test"
    )
    test_db.add(log)
    await test_db.commit()

    # Check response headers indicate streaming
    response = await client.get("/api/export")
    assert response.status_code == 200
    assert response.headers['content-type'] == 'text/csv; charset=utf-8'
    assert 'attachment' in response.headers.get('content-disposition', '')


@pytest.mark.asyncio
async def test_export_large_dataset(client, test_db):
    """Export with 10k logs completes without memory error."""
    # Use bulk_insert_mappings for performance
    now = datetime.now(timezone.utc)
    logs_data = []
    for i in range(10000):
        logs_data.append({
            'timestamp': now + timedelta(seconds=i),
            'severity': 'INFO',
            'source': 'test-service',
            'message': f'Large dataset message {i}'
        })

    # Insert in bulk
    await test_db.run_sync(
        lambda session: session.bulk_insert_mappings(Log, logs_data)
    )
    await test_db.commit()

    # Export all logs
    response = await client.get("/api/export")
    assert response.status_code == 200

    # Parse CSV
    rows = parse_csv_response(response.content)
    assert len(rows) == 10001  # header + 10k data rows


# EXPORT-03 tests (CSV format)


@pytest.mark.asyncio
async def test_export_csv_headers(client, test_db):
    """CSV header row is exactly 'Timestamp,Severity,Source,Message'."""
    # Create one log
    log = Log(
        timestamp=datetime.now(timezone.utc),
        severity="INFO",
        source="test-service",
        message="Test"
    )
    test_db.add(log)
    await test_db.commit()

    # Export
    response = await client.get("/api/export")
    assert response.status_code == 200

    # Parse CSV
    rows = parse_csv_response(response.content)
    assert rows[0] == ['Timestamp', 'Severity', 'Source', 'Message']


@pytest.mark.asyncio
async def test_export_csv_field_values(client, test_db):
    """CSV data rows contain correct values in correct order."""
    timestamp = datetime(2025, 3, 22, 14, 30, 0, tzinfo=timezone.utc)
    log = Log(
        timestamp=timestamp,
        severity="ERROR",
        source="api-service",
        message="Database connection failed"
    )
    test_db.add(log)
    await test_db.commit()

    # Export
    response = await client.get("/api/export")
    rows = parse_csv_response(response.content)

    # Verify data row
    data_row = rows[1]
    assert data_row[0] == timestamp.isoformat()
    assert data_row[1] == "ERROR"
    assert data_row[2] == "api-service"
    assert data_row[3] == "Database connection failed"


@pytest.mark.asyncio
async def test_export_csv_timestamp_format(client, test_db):
    """CSV timestamp format is ISO 8601."""
    timestamp = datetime(2025, 3, 22, 14, 30, 0, tzinfo=timezone.utc)
    log = Log(
        timestamp=timestamp,
        severity="INFO",
        source="test-service",
        message="Test"
    )
    test_db.add(log)
    await test_db.commit()

    # Export
    response = await client.get("/api/export")
    rows = parse_csv_response(response.content)

    # Verify ISO 8601 format (contains 'T' and timezone)
    timestamp_str = rows[1][0]
    assert 'T' in timestamp_str
    assert '+00:00' in timestamp_str or timestamp_str.endswith('Z')


@pytest.mark.asyncio
async def test_export_csv_special_characters(client, test_db):
    """CSV handles special characters (commas, quotes, newlines)."""
    log = Log(
        timestamp=datetime.now(timezone.utc),
        severity="ERROR",
        source="test-service",
        message='Error occurred: connection failed, retry in 5s.\nStack: "ValueError"'
    )
    test_db.add(log)
    await test_db.commit()

    # Export
    response = await client.get("/api/export")
    rows = parse_csv_response(response.content)

    # Verify csv.reader correctly parsed the message with special characters
    message = rows[1][3]
    assert 'connection failed, retry in 5s.' in message
    assert '"ValueError"' in message


# Edge case tests


@pytest.mark.asyncio
async def test_export_invalid_severity(client, test_db):
    """Export with invalid severity returns 400 error."""
    response = await client.get("/api/export?severity=INVALID")
    assert response.status_code == 400
    error = response.json()
    assert 'Invalid severity' in error['detail']


@pytest.mark.asyncio
async def test_export_empty_result(client, test_db):
    """Export with empty result set returns header-only CSV."""
    # Create only INFO logs
    log = Log(
        timestamp=datetime.now(timezone.utc),
        severity="INFO",
        source="test-service",
        message="Test"
    )
    test_db.add(log)
    await test_db.commit()

    # Export with impossible filter
    response = await client.get("/api/export?severity=ERROR")
    assert response.status_code == 200

    # Parse CSV
    rows = parse_csv_response(response.content)
    assert len(rows) == 1  # Only header row
    assert rows[0] == ['Timestamp', 'Severity', 'Source', 'Message']


@pytest.mark.asyncio
async def test_export_50k_limit(client, test_db):
    """Export respects 50k row limit."""
    # Use bulk_insert_mappings to create 50,001 logs
    now = datetime.now(timezone.utc)
    logs_data = []
    for i in range(50001):
        logs_data.append({
            'timestamp': now + timedelta(seconds=i),
            'severity': 'INFO',
            'source': 'test-service',
            'message': f'Message {i}'
        })

    # Insert in bulk
    await test_db.run_sync(
        lambda session: session.bulk_insert_mappings(Log, logs_data)
    )
    await test_db.commit()

    # Export all logs
    response = await client.get("/api/export")
    assert response.status_code == 200

    # Parse CSV
    rows = parse_csv_response(response.content)
    # Verify exactly 50,000 data rows (+ 1 header = 50,001 total)
    assert len(rows) == 50001
