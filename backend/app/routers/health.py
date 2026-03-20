"""
Health check endpoint.

Tests database connectivity and returns service status.
"""
import logging
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint with database connectivity test.

    Tests database connection by executing SELECT 1 query.
    Returns 200 OK if database is reachable, 503 Service Unavailable if not.

    This is a public endpoint with no authentication required.
    Used by Docker health checks and monitoring systems.

    Returns:
        200 OK: {"status": "ok", "database": "connected"}
        503 Service Unavailable: {"status": "unhealthy", "database": "disconnected"}

    Example:
        $ curl http://localhost:8000/api/health
        {"status": "ok", "database": "connected"}
    """
    try:
        # Test database connectivity with SELECT 1 (per CONTEXT.md requirement)
        await db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        # Log error but don't expose database details to client
        # (per CONTEXT.md: "Database connection errors: Return generic 500")
        logger.error(f"Health check failed - database connectivity error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected"
            }
        )
