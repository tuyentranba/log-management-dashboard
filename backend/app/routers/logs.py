"""
Log CRUD endpoints.

Provides POST /api/logs (create), GET /api/logs (list with pagination),
and GET /api/logs/{id} (read single).
"""
from datetime import datetime
from typing import Annotated, Optional
import csv
import io
import anyio
from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_

from ..dependencies import get_db
from ..models import Log
from ..schemas.logs import LogCreate, LogResponse, LogListResponse
from ..utils.cursor import encode_cursor, decode_cursor

router = APIRouter()


async def generate_csv_rows(logs_stream):
    """
    Async generator that yields CSV content incrementally.

    Args:
        logs_stream: SQLAlchemy scalars stream from AsyncResult

    Yields:
        str: CSV content chunks (UTF-8 BOM, header, then row by row)
    """
    # Create StringIO buffer and csv.writer instance
    output = io.StringIO()
    writer = csv.writer(output)

    # Yield UTF-8 BOM first (Excel compatibility)
    yield '\ufeff'

    # Write header row with Title Case
    writer.writerow(['Timestamp', 'Severity', 'Source', 'Message'])
    yield output.getvalue()
    output.truncate(0)
    output.seek(0)

    # Async iterate over logs_stream
    async for log in logs_stream:
        # Write row with ISO 8601 timestamp format
        writer.writerow([
            log.timestamp.isoformat(),
            log.severity,
            log.source,
            log.message
        ])
        yield output.getvalue()
        output.truncate(0)
        output.seek(0)

        # Provide cancellation point (required for FastAPI cancellation protocol)
        await anyio.sleep(0)


@router.post("/logs", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(
    log_data: LogCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new log entry.

    Args:
        log_data: Log data from request body (validated by Pydantic)
        db: Database session (injected)

    Returns:
        Created log object with server-generated id

    Raises:
        422: Validation error (missing required fields, invalid severity, timezone-naive timestamp)
    """
    # Create SQLAlchemy model instance from validated Pydantic model
    log = Log(
        timestamp=log_data.timestamp,
        message=log_data.message,
        severity=log_data.severity,
        source=log_data.source
    )

    # Persist to database
    db.add(log)
    await db.commit()
    await db.refresh(log)  # Load server-generated id

    return log


@router.get("/logs", response_model=LogListResponse)
async def list_logs(
    # Filtering parameters
    severity: Annotated[Optional[list[str]], Query()] = None,
    source: Annotated[Optional[str], Query()] = None,
    search: Annotated[Optional[str], Query()] = None,
    date_from: Annotated[Optional[datetime], Query()] = None,
    date_to: Annotated[Optional[datetime], Query()] = None,
    # Sorting parameters
    sort: Annotated[str, Query(pattern="^(timestamp|severity|source)$")] = "timestamp",
    order: Annotated[str, Query(pattern="^(asc|desc)$")] = "desc",
    # Pagination parameters
    cursor: Annotated[Optional[str], Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    List logs with cursor-based pagination, filtering, and sorting.

    Filters:
        severity: One or more severity levels (repeat parameter: ?severity=ERROR&severity=WARNING)
        source: Source identifier (case-insensitive partial match)
        date_from: Start of date range (inclusive, ISO 8601 with timezone)
        date_to: End of date range (inclusive, ISO 8601 with timezone)

    Sorting:
        sort: Field to sort by (timestamp, severity, or source)
        order: Sort direction (asc or desc)

    Pagination:
        cursor: Opaque pagination cursor from previous response
        limit: Number of logs per page (1-200, default 50)

    Returns:
        Paginated list with data, next_cursor, and has_more

    Raises:
        400: Invalid cursor format or invalid severity value
        422: Invalid query parameters (limit, sort field, order)
    """
    # Start with base query
    query = select(Log)

    # Apply filters
    if severity:
        # Validate severity values per CONTEXT.md specification
        valid_severities = {"INFO", "WARNING", "ERROR", "CRITICAL"}
        for sev in severity:
            if sev not in valid_severities:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid severity: {sev}. Must be one of: {', '.join(sorted(valid_severities))}"
                )
        query = query.where(Log.severity.in_(severity))

    if source:
        # Case-insensitive partial match using ILIKE
        # Note: ILIKE bypasses indexes (acceptable for MVP, documented in RESEARCH.md Pitfall 3)
        query = query.where(Log.source.ilike(f"%{source}%"))

    if search:
        # Case-insensitive partial match using ILIKE
        # Note: ILIKE bypasses indexes (acceptable for MVP, documented in RESEARCH.md Pitfall 3)
        query = query.where(Log.message.ilike(f"%{search}%"))

    if date_from:
        query = query.where(Log.timestamp >= date_from)

    if date_to:
        query = query.where(Log.timestamp <= date_to)

    # Apply sorting
    sort_column = getattr(Log, sort)
    if order == "desc":
        sort_direction = sort_column.desc()
    else:
        sort_direction = sort_column.asc()

    # Always include id as secondary sort for stable ordering (prevents cursor pagination issues)
    query = query.order_by(
        sort_direction,
        Log.id.desc() if order == "desc" else Log.id.asc()
    )

    # Apply cursor pagination
    if cursor:
        try:
            cursor_value, cursor_id = decode_cursor(cursor)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Composite cursor comparison based on sort direction
        # Note: cursor_value represents the sorted field (timestamp, severity, or source)
        if order == "desc":
            query = query.where(
                or_(
                    sort_column < cursor_value,
                    and_(sort_column == cursor_value, Log.id < cursor_id)
                )
            )
        else:
            query = query.where(
                or_(
                    sort_column > cursor_value,
                    and_(sort_column == cursor_value, Log.id > cursor_id)
                )
            )

    # Fetch limit + 1 to determine if more pages exist
    query = query.limit(limit + 1)
    result = await db.execute(query)
    logs = list(result.scalars().all())

    # Check if more pages exist
    has_more = len(logs) > limit
    if has_more:
        logs = logs[:limit]

    # Generate next cursor from last item using sorted field value
    next_cursor = None
    if has_more and logs:
        last_log = logs[-1]
        cursor_value = getattr(last_log, sort)
        next_cursor = encode_cursor(cursor_value, last_log.id)

    return LogListResponse(
        data=logs,
        next_cursor=next_cursor,
        has_more=has_more
    )


@router.get("/logs/{log_id}", response_model=LogResponse)
async def get_log(
    log_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single log by ID.

    Args:
        log_id: Log primary key from URL path
        db: Database session (injected)

    Returns:
        Log object with all fields

    Raises:
        404: Log with given id does not exist
        422: log_id is not a valid integer (FastAPI automatic)
    """
    # Query database by primary key
    log = await db.get(Log, log_id)

    # Return 404 if not found
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log with id {log_id} not found"
        )

    return log


@router.put("/logs/{log_id}", response_model=LogResponse)
async def update_log(
    log_id: int,
    log_data: LogCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing log entry with full replacement.

    Args:
        log_id: Log primary key from URL path
        log_data: Complete log data (all fields required)
        db: Database session (injected)

    Returns:
        Updated log object with all fields

    Raises:
        404: Log with given id does not exist
        422: Validation error (invalid timestamp, severity, etc.)
    """
    # Query database by primary key
    log = await db.get(Log, log_id)

    # Return 404 if not found
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log with id {log_id} not found"
        )

    # Update all fields (full replacement per CONTEXT.md decision 3)
    log.timestamp = log_data.timestamp
    log.message = log_data.message
    log.severity = log_data.severity
    log.source = log_data.source

    # Persist changes
    await db.commit()
    await db.refresh(log)

    return log


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(
    log_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a log entry permanently.

    Args:
        log_id: Log primary key from URL path
        db: Database session (injected)

    Returns:
        204 No Content on successful deletion

    Raises:
        404: Log with given id does not exist
    """
    # Query database by primary key
    log = await db.get(Log, log_id)

    # Return 404 if not found
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log with id {log_id} not found"
        )

    # Delete from database (hard delete per CONTEXT.md decision 4)
    await db.delete(log)
    await db.commit()

    # 204 No Content - no response body needed
    return None


@router.get("/export")
async def export_logs_csv(
    # Same filter parameters as list_logs
    severity: Annotated[Optional[list[str]], Query()] = None,
    source: Annotated[Optional[str], Query()] = None,
    search: Annotated[Optional[str], Query()] = None,
    date_from: Annotated[Optional[datetime], Query()] = None,
    date_to: Annotated[Optional[datetime], Query()] = None,
    sort: Annotated[str, Query(pattern="^(timestamp|severity|source)$")] = "timestamp",
    order: Annotated[str, Query(pattern="^(asc|desc)$")] = "desc",
    db: AsyncSession = Depends(get_db)
):
    """
    Export filtered logs as CSV with streaming response.

    Accepts same filter parameters as list_logs endpoint to ensure WYSIWYG
    (What You See Is What You Get) - exported data matches UI view.

    Parameters:
        severity: One or more severity levels (repeat parameter: ?severity=ERROR&severity=WARNING)
        source: Source identifier (case-insensitive partial match)
        date_from: Start of date range (inclusive, ISO 8601 with timezone)
        date_to: End of date range (inclusive, ISO 8601 with timezone)
        sort: Field to sort by (timestamp, severity, or source)
        order: Sort direction (asc or desc)
        db: Database session (injected)

    Returns:
        StreamingResponse with CSV content (media_type: text/csv)

    Raises:
        400: Invalid filter parameters (invalid severity value)
    """
    # Build query using EXACT same filtering logic as list_logs
    query = select(Log)

    # Apply filters - same validation and filtering logic
    if severity:
        # Validate severity values per CONTEXT.md specification
        valid_severities = {"INFO", "WARNING", "ERROR", "CRITICAL"}
        for sev in severity:
            if sev not in valid_severities:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid severity: {sev}. Must be one of: {', '.join(sorted(valid_severities))}"
                )
        query = query.where(Log.severity.in_(severity))

    if source:
        # Case-insensitive partial match using ILIKE
        query = query.where(Log.source.ilike(f"%{source}%"))

    if search:
        # Case-insensitive partial match using ILIKE
        query = query.where(Log.message.ilike(f"%{search}%"))

    if date_from:
        query = query.where(Log.timestamp >= date_from)

    if date_to:
        query = query.where(Log.timestamp <= date_to)

    # Apply sorting - same sort logic as list_logs
    sort_column = getattr(Log, sort)
    if order == "desc":
        sort_direction = sort_column.desc()
    else:
        sort_direction = sort_column.asc()

    # Always include id as secondary sort for stable ordering
    query = query.order_by(
        sort_direction,
        Log.id.desc() if order == "desc" else Log.id.asc()
    )

    # Hard limit at 50,000 rows per CONTEXT.md decision
    query = query.limit(50000)

    # Stream results from database (yield_per for batch fetching)
    result = await db.stream(query.execution_options(yield_per=1000))
    logs_stream = result.scalars()

    # Generate filename with timestamp
    filename = f"logs-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.csv"

    return StreamingResponse(
        generate_csv_rows(logs_stream),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
