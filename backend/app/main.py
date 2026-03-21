import logging
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import settings
from .database import engine, AsyncSessionLocal
from .routers import health, logs


# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    Tests database connectivity on startup.
    """
    # Startup: Test database connectivity
    logger.info("Application starting up...")
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

    yield

    # Shutdown: Close database connections
    logger.info("Application shutting down...")
    await engine.dispose()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Logs Dashboard API",
    description="Log management and analytics REST API",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS (explicit origins, not wildcard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Explicit list from environment
    allow_credentials=True,  # Required for future auth
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],  # Accept-*, Content-Type always allowed
)


# Custom exception handler for validation errors (API-08 requirement)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle validation errors with request ID.

    Returns 400 Bad Request with detailed error information.
    Logs validation errors as WARNING per CONTEXT.md.
    """
    request_id = str(uuid.uuid4())
    logger.warning(
        f"Validation error {request_id} on {request.method} {request.url.path}: "
        f"{exc.errors()}"
    )

    # Sanitize error details to ensure JSON serializability
    # Remove non-serializable objects from 'ctx' field (e.g., Exception instances)
    errors = []
    for error in exc.errors():
        error_copy = dict(error)
        if 'ctx' in error_copy and 'error' in error_copy['ctx']:
            # Convert error object to string
            error_copy['ctx'] = {k: str(v) if k == 'error' else v
                                for k, v in error_copy['ctx'].items()}
        errors.append(error_copy)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": errors,  # Sanitized error details
            "request_id": request_id
        }
    )


# Generic exception handler for unhandled errors (API-08 requirement)
@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle unhandled exceptions with request ID.

    Returns 500 Internal Server Error without exposing details.
    Logs server errors as ERROR per CONTEXT.md.
    """
    request_id = str(uuid.uuid4())
    logger.error(
        f"Server error {request_id} on {request.method} {request.url.path}: "
        f"{str(exc)}",
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",  # Generic, no DB details exposed
            "request_id": request_id
        }
    )


# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(logs.router, prefix="/api", tags=["logs"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - redirects to /docs for API documentation."""
    return {
        "message": "Logs Dashboard API",
        "docs": "/docs",
        "health": "/api/health"
    }
