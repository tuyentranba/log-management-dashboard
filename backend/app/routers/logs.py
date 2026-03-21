"""
Log CRUD endpoints.

Provides POST /api/logs (create) and GET /api/logs/{id} (read single).
"""
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..models import Log
from ..schemas.logs import LogCreate, LogResponse

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
