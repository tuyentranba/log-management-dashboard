"""
Log CRUD endpoints.

Provides POST /api/logs (create), GET /api/logs (list with pagination),
and GET /api/logs/{id} (read single).
"""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_

from ..dependencies import get_db
from ..models import Log
from ..schemas.logs import LogCreate, LogResponse, LogListResponse
from ..utils.cursor import encode_cursor, decode_cursor

router = APIRouter()


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
    cursor: Annotated[Optional[str], Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    List logs with cursor-based pagination.

    Args:
        cursor: Opaque pagination cursor from previous response (optional)
        limit: Number of logs per page (1-200, default 50)
        db: Database session (injected)

    Returns:
        Paginated list with data, next_cursor, and has_more

    Raises:
        400: Invalid cursor format
        422: Invalid limit (< 1 or > 200)
    """
    # Start with base query ordered by timestamp DESC, id DESC for stable sorting
    query = select(Log).order_by(Log.timestamp.desc(), Log.id.desc())

    # Apply cursor filter if provided
    if cursor:
        try:
            cursor_timestamp, cursor_id = decode_cursor(cursor)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Composite cursor comparison: (timestamp, id) < (cursor_timestamp, cursor_id)
        # Using OR for descending sort: timestamp < cursor OR (timestamp = cursor AND id < cursor_id)
        query = query.where(
            or_(
                Log.timestamp < cursor_timestamp,
                and_(Log.timestamp == cursor_timestamp, Log.id < cursor_id)
            )
        )

    # Fetch limit + 1 to determine if more pages exist
    query = query.limit(limit + 1)
    result = await db.execute(query)
    logs = list(result.scalars().all())

    # Check if more pages exist
    has_more = len(logs) > limit
    if has_more:
        logs = logs[:limit]  # Trim to actual page size

    # Generate next cursor from last item
    next_cursor = None
    if has_more and logs:
        last_log = logs[-1]
        next_cursor = encode_cursor(last_log.timestamp, last_log.id)

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
