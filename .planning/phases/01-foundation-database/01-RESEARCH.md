# Phase 1: Foundation & Database - Research

**Researched:** 2026-03-20
**Domain:** PostgreSQL database schema, Docker infrastructure, FastAPI foundation
**Confidence:** HIGH

## Summary

Phase 1 establishes the technical foundation for the entire log management system. Research focused on production-ready PostgreSQL indexing strategies, Docker Compose multi-service orchestration, FastAPI async configuration, and high-performance bulk data loading. The stack (FastAPI 0.135.1 + SQLAlchemy 2.0.48 async + PostgreSQL 18 + Docker Compose) is mature and well-documented with clear patterns for the required infrastructure.

**Primary recommendation:** Use async-first architecture throughout (AsyncEngine, AsyncSession, async endpoints), implement BRIN + composite indexes from day one, configure explicit CORS origins, and use PostgreSQL COPY or SQLAlchemy bulk operations for seed script performance.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Error Response Format:**
- Use FastAPI's default format: `{"detail": "message"}` for single errors
- Validation errors: Use FastAPI's default detailed array with `loc`, `msg`, `type` fields
- No stack traces in responses (production-safe, clean responses)
- Include request IDs in error responses for tracing/debugging
- Standard REST HTTP status codes: 400 (validation), 404 (not found), 500 (server error)
- Database connection errors: Return generic 500 "Internal server error" without exposing DB details
- Validation messages: User-friendly tone ("Severity must be INFO, WARNING, ERROR, or CRITICAL")
- Allow duplicate log entries (logs are append-only, no conflict detection)
- Server-side error logging with levels: 400s logged as WARNING, 500s logged as ERROR

**Health Check Endpoint:**
- Endpoint: `GET /api/health`
- Response format: `{"status": "ok", "database": "connected"}`
- Test database connectivity: Execute `SELECT 1` query to validate DB is reachable
- Public endpoint: No authentication required (standard practice for health checks)
- Unhealthy state: Return HTTP 503 Service Unavailable when DB connection fails

**Docker Configuration:**
- Services: 3 services (postgres, backend, frontend)
- Volumes: Bind mounts for `./backend` and `./frontend` to enable hot-reload during development
- Database volume: Named volume `postgres_data` for persistence
- Environment variables: Managed via `.env` file (provide `.env.example` in repo)
- Hot-reload: Frontend uses Next.js dev server with fast refresh
- Compose files: Single `docker-compose.yml` (sufficient for demo/portfolio project)
- Health checks: Define healthcheck for postgres and backend services
- Database initialization: Automatic via init script or migrations on container startup
- Developer commands: Provide Makefile with shortcuts (`make start`, `make test`, `make seed`)

**Seed Data Generation:**
- Message realism: Template-based realistic patterns ("User login failed", "API request timeout", "Database query slow")
- Severity distribution: Realistic production ratio
  - 70% INFO
  - 20% WARNING
  - 8% ERROR
  - 2% CRITICAL
- Sources: 5-10 different sources representing microservices architecture (api-service, auth-service, database, frontend, worker, cache, queue)
- Timestamp distribution: Evenly spread across last 30 days with realistic daily patterns
- Target: 100k logs generated in under 60 seconds (bulk insert performance)

### Claude's Discretion

- Exact Docker image versions (use latest stable)
- FastAPI project structure (routers, dependencies, middleware)
- Database migration tool choice (Alembic or raw SQL)
- Seed script implementation details (Python faker library, batch size)
- Logging library configuration (structlog, python-json-logger, or standard logging)

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DB-01 | Database schema includes logs table with id, timestamp, message, severity, source columns | SQLAlchemy declarative models, timestamptz type, async table creation patterns |
| DB-02 | Timestamp column uses timestamptz (timezone-aware) data type | PostgreSQL timestamptz stores UTC internally, prevents timezone-related bugs in analytics |
| DB-03 | Database has BRIN index on timestamp column for time-series queries | BRIN indexes optimal for sequential timestamp data, pages_per_range=128 default |
| DB-04 | Database has B-tree indexes on severity and source columns | B-tree default index type, efficient for equality filtering |
| DB-05 | Database has composite index on (timestamp, severity, source) for filtered queries | Composite index with DESC timestamp, column order matters for query planner |
| DB-06 | Seed script populates database with realistic demo data (10k-100k logs) | PostgreSQL COPY command or SQLAlchemy bulk operations achieve <60s for 100k rows |
| INFRA-01 | Application runs via docker-compose with all services | Docker Compose service definitions with depends_on and health checks |
| INFRA-02 | Docker setup includes backend, database, and frontend services | Multi-service orchestration with networking and volume configuration |
| INFRA-03 | Services can be started with single command | `docker-compose up` with Makefile shortcuts for developer ergonomics |
| INFRA-04 | Environment variables used for configuration | pydantic-settings for type-safe .env loading, Docker env_file support |
| API-07 | All API endpoints include input validation | Pydantic models with FastAPI automatic validation |
| API-08 | API returns meaningful error messages with appropriate HTTP status codes | HTTPException with 400/404/500, custom exception handlers |
| API-09 | CORS is properly configured for frontend access | Explicit allow_origins list, allow_credentials for auth-ready setup |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PostgreSQL | 18.x | Relational database | Most advanced open-source RDBMS, mature BRIN/composite index support, proven time-series performance |
| FastAPI | 0.135.1 | Python async API framework | Modern ASGI with automatic validation, OpenAPI docs, native async support, industry standard 2025 |
| SQLAlchemy | 2.0.48 | Async ORM | Industry-standard ORM with mature async support (AsyncSession, AsyncEngine), Alembic integration |
| psycopg | 3.3.3 | PostgreSQL async adapter | Modern async driver (successor to psycopg2), required for SQLAlchemy async with PostgreSQL |
| Pydantic | 2.12.5 | Data validation | Integrated with FastAPI for request/response validation, 5-50x faster than v1 |
| Docker Compose | 2.x | Multi-container orchestration | Standard tool for local dev environments, simplifies postgres+backend+frontend coordination |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Alembic | 1.18.4 | Database migrations | Always. Official SQLAlchemy migration tool, handles schema versioning with confidence |
| pydantic-settings | 2.13.1 | Configuration management | Always. Type-safe environment variable loading with .env file support |
| Uvicorn | 0.42.0 | ASGI server | Always. Lightning-fast server for running FastAPI, use --workers for production |
| pytest | 9.0.2 | Testing framework | Always. Industry standard for Python testing, extensive plugin ecosystem |
| pytest-asyncio | 1.3.0 | Async test support | For testing async FastAPI endpoints, allows await in test functions |
| httpx | 0.28.1 | HTTP client | For FastAPI TestClient and testing API endpoints with async support |
| Ruff | 0.15.7 | Linting & formatting | Replaces Black + Flake8 + isort, 10-100x faster, used by FastAPI itself |
| mypy | 1.19.1 | Static type checking | Catch type errors before runtime, essential for maintaining FastAPI type safety |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Alembic | Raw SQL migrations | Alembic provides versioning, rollback, and autogenerate features; raw SQL requires manual tracking |
| psycopg3 | psycopg2 | psycopg2 is legacy with no native async; requires gevent/threading hacks with FastAPI |
| Ruff | Black + Flake8 + isort | Separate tools are slower, require configuring 3 configs; Ruff consolidates and accelerates |
| BRIN index | B-tree on timestamp | B-tree is larger (10-100x) but faster for random access; BRIN optimal for sequential time-series |

**Installation:**
```bash
# Backend requirements.txt
fastapi==0.135.1
uvicorn[standard]==0.42.0
sqlalchemy==2.0.48
psycopg==3.3.3
alembic==1.18.4
pydantic==2.12.5
pydantic-settings==2.13.1

# Development requirements-dev.txt
ruff==0.15.7
mypy==1.19.1
pytest==9.0.2
pytest-asyncio==1.3.0
httpx==0.28.1
```

## Architecture Patterns

### Recommended Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app instance, CORS, error handlers
│   ├── config.py            # pydantic-settings configuration
│   ├── database.py          # AsyncEngine, AsyncSession factory
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response models
│   ├── dependencies.py      # Shared dependencies (get_db session)
│   └── routers/
│       ├── __init__.py
│       └── health.py        # Health check endpoint
├── alembic/
│   ├── env.py               # Alembic async configuration
│   └── versions/            # Migration scripts
├── scripts/
│   └── seed.py              # Database seeding script
├── tests/
│   ├── conftest.py          # Pytest fixtures (test db, client)
│   └── test_health.py       # Health endpoint tests
├── alembic.ini              # Alembic configuration
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
└── Dockerfile               # Production container image

docker-compose.yml           # Multi-service orchestration
.env.example                 # Example environment variables
Makefile                     # Developer shortcuts
```

### Pattern 1: SQLAlchemy Async Configuration
**What:** Configure AsyncEngine and AsyncSession for FastAPI dependency injection
**When to use:** Always in Phase 1 setup

**Example:**
```python
# Source: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Create async engine with connection pooling
engine = create_async_engine(
    "postgresql+psycopg://user:password@postgres:5432/logs_db",
    echo=True,  # SQL logging for development
    pool_size=20,  # Persistent connections
    max_overflow=10,  # Additional temporary connections
    pool_pre_ping=True,  # Validate connections on checkout
    pool_recycle=3600  # Recycle connections after 1 hour
)

# Create session factory with expire_on_commit=False
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False  # Prevents attribute expiration after commit
)

# FastAPI dependency for session injection
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### Pattern 2: FastAPI CORS Configuration
**What:** Explicit origin allowlist for secure cross-origin requests
**When to use:** Always in Phase 1 when setting up FastAPI app

**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/cors/
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# NEVER use wildcard ["*"] with credentials
origins = [
    "http://localhost:3000",  # Next.js dev server
    "http://localhost:8080",  # Alternative frontend port
    # Production origin added via environment variable
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Explicit list, not wildcard
    allow_credentials=True,  # Required for future auth
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],  # Accept-*, Content-Type always allowed
)
```

### Pattern 3: FastAPI Error Handling
**What:** Custom exception handlers for consistent error responses
**When to use:** Always in Phase 1 for API-08 requirement

**Example:**
```python
# Source: https://fastapi.tiangolo.com/tutorial/handling-errors/
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uuid

app = FastAPI()

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = str(uuid.uuid4())
    # Log validation errors as WARNING (per user decision)
    logger.warning(f"Validation error {request_id}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": exc.errors(),  # FastAPI default format with loc, msg, type
            "request_id": request_id
        }
    )

# Generic exception handler for unhandled errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid.uuid4())
    # Log server errors as ERROR (per user decision)
    logger.error(f"Server error {request_id}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",  # Generic message, no DB details exposed
            "request_id": request_id
        }
    )
```

### Pattern 4: Health Check with Database Connectivity Test
**What:** Health endpoint that verifies database connection
**When to use:** Always in Phase 1 for INFRA requirements

**Example:**
```python
# Source: FastAPI docs + user requirements from CONTEXT.md
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Test database connectivity with SELECT 1
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        # Return 503 Service Unavailable when DB connection fails
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "disconnected"}
        )
```

### Pattern 5: PostgreSQL Index Creation
**What:** Create BRIN, B-tree, and composite indexes for optimal query performance
**When to use:** Always in initial migration or table creation

**Example:**
```sql
-- Source: https://www.postgresql.org/docs/current/sql-createindex.html
-- https://www.postgresql.org/docs/current/indexes-multicolumn.html

-- BRIN index on timestamp for time-series queries (very small, fast for sequential data)
CREATE INDEX idx_logs_timestamp_brin ON logs USING BRIN (timestamp)
  WITH (pages_per_range = 128, autosummarize = on);

-- B-tree indexes on frequently filtered columns
CREATE INDEX idx_logs_severity ON logs (severity);
CREATE INDEX idx_logs_source ON logs (source);

-- Composite index for multi-column filtering (timestamp DESC for recent logs first)
-- Column order: timestamp (highest cardinality, range queries), severity, source
CREATE INDEX idx_logs_composite ON logs (timestamp DESC, severity, source);

-- For production: Use CONCURRENTLY to avoid locking (Phase 1 doesn't need this for initial creation)
-- CREATE INDEX CONCURRENTLY idx_logs_composite ON logs (timestamp DESC, severity, source);
```

### Pattern 6: Bulk Insert for Seed Script
**What:** High-performance bulk insert using SQLAlchemy or PostgreSQL COPY
**When to use:** Always for seed script to achieve <60 second target for 100k logs

**Example:**
```python
# Source: https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html
# https://www.postgresql.org/docs/current/sql-copy.html
from sqlalchemy import insert
from datetime import datetime, timedelta
import random

async def seed_database(session: AsyncSession, count: int = 100000):
    """Generate and insert 100k logs in under 60 seconds"""

    # Template-based realistic log messages
    message_templates = [
        "User login failed for user_{id}",
        "API request timeout on endpoint /api/users",
        "Database query slow: {duration}ms",
        "Cache miss for key: user_session_{id}",
        "Worker task completed: process_data",
    ]

    # Realistic severity distribution (70/20/8/2)
    severities = (
        ["INFO"] * 70 +
        ["WARNING"] * 20 +
        ["ERROR"] * 8 +
        ["CRITICAL"] * 2
    )

    sources = [
        "api-service", "auth-service", "database",
        "frontend", "worker", "cache", "queue"
    ]

    # Generate all log records in memory first (fast)
    base_time = datetime.utcnow() - timedelta(days=30)
    logs = []
    for i in range(count):
        logs.append({
            "timestamp": base_time + timedelta(seconds=i * 25),  # Spread across 30 days
            "message": random.choice(message_templates).format(id=i, duration=random.randint(10, 5000)),
            "severity": random.choice(severities),
            "source": random.choice(sources)
        })

    # Bulk insert using SQLAlchemy (automatically batches)
    # Alternative: Use PostgreSQL COPY for even faster inserts
    await session.execute(insert(Log), logs)
    await session.commit()
```

### Pattern 7: Docker Compose Multi-Service Setup
**What:** Orchestrate postgres, backend, frontend with health checks and hot-reload
**When to use:** Always in Phase 1 for INFRA requirements

**Example:**
```yaml
# Source: https://docs.docker.com/compose/compose-file/05-services/
version: '3.8'

services:
  postgres:
    image: postgres:18-alpine
    environment:
      POSTGRES_DB: logs_db
      POSTGRES_USER: logs_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U logs_user -d logs_db"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app:rw  # Bind mount for hot-reload
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy  # Wait for postgres health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend:/app:rw  # Bind mount for Next.js fast refresh
      - /app/node_modules  # Prevent overwriting node_modules
    ports:
      - "3000:3000"
    env_file:
      - .env
    depends_on:
      - backend

volumes:
  postgres_data:  # Named volume for database persistence
```

### Pattern 8: pydantic-settings Configuration
**What:** Type-safe environment variable loading with .env file support
**When to use:** Always in Phase 1 for INFRA-04 requirement

**Example:**
```python
# Source: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    # Database configuration
    database_url: PostgresDsn = Field(
        validation_alias='DATABASE_URL',
        description="PostgreSQL connection string"
    )

    # CORS configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        validation_alias='CORS_ORIGINS'
    )

    # Server configuration
    debug: bool = False
    log_level: str = "INFO"

# Create global settings instance
settings = Settings()
```

### Pattern 9: Alembic Async Migration Setup
**What:** Configure Alembic for SQLAlchemy async with proper env.py
**When to use:** Always in Phase 1 if using Alembic for migrations

**Example:**
```python
# Source: https://alembic.sqlalchemy.org/en/latest/tutorial.html
# alembic/env.py for async support
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.database import DATABASE_URL
from app.models import Base

async def run_migrations_online():
    """Run migrations in 'online' mode with async engine."""
    connectable = create_async_engine(DATABASE_URL)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()
```

### Pattern 10: pytest Async Fixtures for Database Testing
**What:** Setup test database and async client for testing FastAPI endpoints
**When to use:** Always in Phase 1 for TEST requirements

**Example:**
```python
# Source: https://docs.pytest.org/en/stable/how-to/fixtures.html
# tests/conftest.py
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient
from app.main import app
from app.database import get_db, Base

# Test database URL
TEST_DATABASE_URL = "postgresql+psycopg://test_user:test_pass@localhost:5432/test_logs_db"

@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create test database and tables for each test"""
    engine = create_async_engine(TEST_DATABASE_URL)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    yield async_session

    # Cleanup: Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def client(test_db):
    """Create async test client with overridden database dependency"""
    async def override_get_db():
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
```

### Anti-Patterns to Avoid

- **Using psycopg2 instead of psycopg3:** Legacy driver has no native async support, requires threading hacks with FastAPI
- **Wildcard CORS origins with credentials:** Setting `allow_origins=["*"]` blocks credential-based requests and creates security vulnerabilities
- **Missing pool_pre_ping:** Without connection validation, database restarts cause errors until pool recycles connections naturally
- **OFFSET-based pagination:** Use cursor-based pagination from the start (Phase 2) to prevent performance degradation with large datasets
- **timestamp without time zone:** Always use timestamptz to prevent timezone-related bugs in analytics (PostgreSQL stores UTC internally)
- **Missing composite index:** Single-column indexes on timestamp, severity, source won't be efficiently combined by query planner for multi-column filters
- **Loading entire result set for CSV export:** Use streaming response (Phase 4) to prevent out-of-memory errors

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Environment variable loading | Custom dotenv parser with validation | pydantic-settings BaseSettings | Type validation, .env file support, PostgresDsn validation, nested config, automatic casting |
| Database migrations | Custom SQL versioning system | Alembic | Schema versioning, autogenerate from models, rollback support, battle-tested with SQLAlchemy |
| Connection pooling | Manual connection management | SQLAlchemy pool_size, max_overflow | Handles connection lifecycle, detects stale connections, optimized for async, production-proven |
| Request validation | Manual type checking and error responses | Pydantic models with FastAPI | Automatic validation, OpenAPI schema generation, detailed error messages with field locations |
| CORS handling | Custom Origin header checking | FastAPI CORSMiddleware | Handles preflight OPTIONS, multiple origins, credential policies, regex patterns |
| Async test fixtures | Manual event loop management | pytest-asyncio with scope fixtures | Proper cleanup, event loop isolation, supports async context managers |
| Health checks in Docker | Custom shell scripts | Docker Compose healthcheck with curl/pg_isready | Standardized, integrates with depends_on conditions, container orchestration systems recognize it |
| Code formatting | Custom style guide enforcement | Ruff (replaces Black + Flake8 + isort) | 10-100x faster, combines linting and formatting, used by FastAPI itself, zero config |

**Key insight:** Infrastructure patterns are mature and well-tested in the Python/FastAPI ecosystem. Custom solutions introduce bugs, require maintenance, and lack community support. Use official tools for configuration, migrations, pooling, and validation.

## Common Pitfalls

### Pitfall 1: Forgetting expire_on_commit=False in AsyncSession
**What goes wrong:** After committing a transaction, accessing SQLAlchemy model attributes triggers implicit async I/O, causing "greenlet_spawn has not been called" errors in FastAPI.

**Why it happens:** SQLAlchemy default behavior expires attributes after commit to ensure fresh data from database. In async contexts, this lazy-loading triggers I/O that violates async patterns.

**How to avoid:** Always set `expire_on_commit=False` when creating async_sessionmaker:
```python
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False  # Critical for async usage
)
```

**Warning signs:** Runtime errors mentioning "greenlet", errors accessing model attributes after commit, inconsistent behavior between tests and production.

### Pitfall 2: Using timestamp Instead of timestamptz
**What goes wrong:** Analytics queries produce different results based on server timezone settings, dashboard charts show incorrect daily counts, DST transitions cause off-by-one-hour errors.

**Why it happens:** PostgreSQL documentation states that `timestamp without time zone` is "given in the time zone specified by the TimeZone configuration parameter." Developers assume timestamps are "just stored as UTC" but PostgreSQL doesn't enforce this.

**How to avoid:** Always use `timestamp with time zone` (timestamptz) for log timestamps:
```python
# SQLAlchemy model
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import TIMESTAMP

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)  # timezone=True for timestamptz
```

**Warning signs:** Analytics counts changing when database timezone changes, hourly aggregations not aligning to boundaries, different results from different clients.

### Pitfall 3: Missing pool_pre_ping Causing Connection Errors After Database Restart
**What goes wrong:** After PostgreSQL restarts or idle connection timeout, application returns "connection closed" errors until connection pool naturally recycles stale connections.

**Why it happens:** Connection pools maintain persistent connections that can become stale if database restarts. Without validation, applications attempt to use dead connections.

**How to avoid:** Always enable `pool_pre_ping=True`:
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True  # Validates connections before use
)
```

**Warning signs:** Intermittent "connection closed" errors after periods of inactivity, errors clearing after retries, connection errors after database maintenance.

### Pitfall 4: BRIN Index Column Ordering Confusion
**What goes wrong:** Developers create composite BRIN index expecting multi-column filtering performance, but BRIN doesn't support multicolumn indexes effectively like B-tree does.

**Why it happens:** Misunderstanding that "BRIN supports multicolumn indexes" means it can be used like B-tree composite indexes. BRIN is optimized for single-column range scans on physically ordered data.

**How to avoid:** Use BRIN only for timestamp column (single-column index), use B-tree composite index for multi-column filtering:
```sql
-- BRIN for time-series timestamp (small, fast for sequential access)
CREATE INDEX idx_logs_timestamp_brin ON logs USING BRIN (timestamp);

-- B-tree composite for multi-column filtering
CREATE INDEX idx_logs_composite ON logs (timestamp DESC, severity, source);
```

**Warning signs:** EXPLAIN ANALYZE showing "Seq Scan" instead of index usage on multi-column filters, BRIN index not being used for queries filtering by severity+source.

### Pitfall 5: Docker Compose depends_on Without Health Check Conditions
**What goes wrong:** Backend service starts before PostgreSQL is ready to accept connections, causing startup failures and requiring manual restarts.

**Why it happens:** Basic `depends_on` only ensures container start order, not readiness. PostgreSQL container may be "started" but still initializing when backend tries to connect.

**How to avoid:** Use `depends_on` with `service_healthy` condition:
```yaml
backend:
  depends_on:
    postgres:
      condition: service_healthy  # Wait for health check to pass
```

**Warning signs:** "connection refused" errors in backend logs on first startup, services requiring manual restart with `docker-compose restart backend`, intermittent startup failures.

### Pitfall 6: Binding node_modules in Docker Compose Volume Mounts
**What goes wrong:** Frontend service fails to start because local machine's node_modules (with potentially different OS/architecture) overwrites container's node_modules.

**Why it happens:** Bind mounting entire project directory (`./frontend:/app`) includes node_modules, overwriting container dependencies that may have native bindings compiled for Linux.

**How to avoid:** Use anonymous volume to protect node_modules:
```yaml
frontend:
  volumes:
    - ./frontend:/app:rw  # Bind mount source code
    - /app/node_modules   # Anonymous volume prevents overwrite
```

**Warning signs:** Module not found errors in frontend container, errors about incompatible binaries, frontend working locally but failing in Docker.

### Pitfall 7: Not Using DATABASE_URL Environment Variable Pattern
**What goes wrong:** Multiple configuration files (alembic.ini, config.py, docker-compose.yml) have duplicate hardcoded database URLs, creating maintenance burden and environment inconsistencies.

**Why it happens:** Different tools (Alembic, SQLAlchemy, Docker) need database URLs, tempting developers to configure each separately instead of centralizing.

**How to avoid:** Use single `DATABASE_URL` environment variable everywhere:
```python
# config.py
database_url: PostgresDsn = Field(validation_alias='DATABASE_URL')

# alembic.ini
sqlalchemy.url = %(DATABASE_URL)s

# docker-compose.yml
environment:
  - DATABASE_URL=postgresql+psycopg://logs_user:${DB_PASSWORD}@postgres:5432/logs_db
```

**Warning signs:** Different database connections in different contexts, configuration drift between tools, difficulty changing database credentials.

### Pitfall 8: Missing Makefile for Developer Ergonomics
**What goes wrong:** Developers need to remember and type long docker-compose commands with various flags, leading to inconsistency and errors.

**Why it happens:** Docker Compose commands are verbose and projects don't prioritize developer experience tooling.

**How to avoid:** Create Makefile with common shortcuts:
```makefile
.PHONY: start stop restart logs test seed clean

start:
	docker-compose up -d

stop:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

test:
	docker-compose exec backend pytest

seed:
	docker-compose exec backend python scripts/seed.py

clean:
	docker-compose down -v
	docker system prune -f
```

**Warning signs:** Team members asking "what's the command to start this?", inconsistent flags used by different developers, typos in frequently-used commands.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 with pytest-asyncio 1.3.0 |
| Config file | pyproject.toml (or pytest.ini in backend/) |
| Quick run command | `pytest tests/test_health.py -v` |
| Full suite command | `pytest tests/ -v --cov=app` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DB-01 | Logs table schema with all required columns | integration | `pytest tests/test_schema.py::test_logs_table_structure -x` | ❌ Wave 0 |
| DB-02 | Timestamp column is timestamptz | integration | `pytest tests/test_schema.py::test_timestamp_timezone_aware -x` | ❌ Wave 0 |
| DB-03 | BRIN index on timestamp exists | integration | `pytest tests/test_schema.py::test_brin_index_exists -x` | ❌ Wave 0 |
| DB-04 | B-tree indexes on severity and source | integration | `pytest tests/test_schema.py::test_btree_indexes_exist -x` | ❌ Wave 0 |
| DB-05 | Composite index on (timestamp, severity, source) | integration | `pytest tests/test_schema.py::test_composite_index_exists -x` | ❌ Wave 0 |
| DB-06 | Seed script populates 100k logs in <60s | performance | `pytest tests/test_seed.py::test_seed_performance -x --timeout=60` | ❌ Wave 0 |
| INFRA-01 | docker-compose up starts all services | manual-only | Manual: `docker-compose up -d && docker-compose ps` | Manual verification |
| INFRA-02 | Three services defined (postgres, backend, frontend) | manual-only | Manual: Check docker-compose.yml structure | Manual verification |
| INFRA-03 | Single command starts services | manual-only | Manual: `make start` (Makefile target) | Manual verification |
| INFRA-04 | Environment variables loaded from .env | integration | `pytest tests/test_config.py::test_env_loading -x` | ❌ Wave 0 |
| API-07 | Health endpoint validates input (no input for /health, but pattern for future) | integration | `pytest tests/test_health.py::test_health_endpoint_validation -x` | ❌ Wave 0 |
| API-08 | Health endpoint returns proper status codes (200/503) | integration | `pytest tests/test_health.py::test_health_status_codes -x` | ❌ Wave 0 |
| API-09 | CORS configured with explicit origins | integration | `pytest tests/test_cors.py::test_cors_configuration -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_health.py -v` (quick smoke test)
- **Per wave merge:** `pytest tests/ -v` (full suite)
- **Phase gate:** Full suite green + manual Docker Compose verification before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_schema.py` — covers DB-01 through DB-05 (database schema and indexes verification)
- [ ] `tests/test_seed.py` — covers DB-06 (seed script performance test with 100k logs)
- [ ] `tests/test_config.py` — covers INFRA-04 (environment variable loading)
- [ ] `tests/test_health.py` — covers API-07, API-08 (health endpoint behavior and status codes)
- [ ] `tests/test_cors.py` — covers API-09 (CORS configuration verification)
- [ ] `tests/conftest.py` — shared fixtures: test_db, async client, test database setup/teardown
- [ ] `pyproject.toml` or `pytest.ini` — pytest configuration with asyncio_mode=auto
- [ ] Framework install: `pip install pytest==9.0.2 pytest-asyncio==1.3.0 httpx==0.28.1` (already in requirements-dev.txt)

## Code Examples

Verified patterns from official sources:

### Database Schema Definition
```python
# Source: SQLAlchemy 2.0 documentation + PostgreSQL timestamptz requirements
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)  # timestamptz
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR, CRITICAL
    source = Column(String(100), nullable=False, index=True)

    def __repr__(self):
        return f"<Log(id={self.id}, severity={self.severity}, source={self.source})>"
```

### Health Check Endpoint Implementation
```python
# Source: https://fastapi.tiangolo.com/tutorial/handling-errors/ + user requirements
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
import logging

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint that verifies database connectivity.

    Returns:
        200 OK: {"status": "ok", "database": "connected"}
        503 Service Unavailable: {"status": "unhealthy", "database": "disconnected"}
    """
    try:
        # Test database connectivity with SELECT 1
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        # Log error but don't expose database details to client
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "disconnected"}
        )
```

### Alembic Initial Migration
```python
# Source: https://alembic.sqlalchemy.org/en/latest/tutorial.html
# alembic/versions/001_create_logs_table.py
"""create logs table with indexes

Revision ID: 001
Revises:
Create Date: 2026-03-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TIMESTAMP

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create logs table
    op.create_table(
        'logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('timestamp', TIMESTAMP(timezone=True), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
    )

    # Create indexes
    # BRIN index on timestamp for time-series queries
    op.execute("""
        CREATE INDEX idx_logs_timestamp_brin ON logs USING BRIN (timestamp)
        WITH (pages_per_range = 128, autosummarize = on)
    """)

    # B-tree indexes on frequently filtered columns
    op.create_index('idx_logs_severity', 'logs', ['severity'])
    op.create_index('idx_logs_source', 'logs', ['source'])

    # Composite index for multi-column filtering
    op.create_index(
        'idx_logs_composite',
        'logs',
        ['timestamp', 'severity', 'source'],
        postgresql_using='btree',
        postgresql_ops={'timestamp': 'DESC'}
    )

def downgrade():
    op.drop_index('idx_logs_composite')
    op.drop_index('idx_logs_source')
    op.drop_index('idx_logs_severity')
    op.execute('DROP INDEX idx_logs_timestamp_brin')
    op.drop_table('logs')
```

### Docker Compose .env File Example
```bash
# Source: https://docs.docker.com/compose/environment-variables/set-environment-variables/
# .env.example (copy to .env and fill in values)

# Database Configuration
DB_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql+psycopg://logs_user:${DB_PASSWORD}@postgres:5432/logs_db

# Backend Configuration
DEBUG=false
LOG_LEVEL=INFO

# CORS Configuration (comma-separated list)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Production (add when deploying)
# CORS_ORIGINS=https://logs-dashboard.example.com
```

### Sample Makefile
```makefile
# Source: Docker Compose best practices + user requirements
.PHONY: help start stop restart logs test seed clean migrate

help:
	@echo "Available commands:"
	@echo "  make start    - Start all services"
	@echo "  make stop     - Stop all services"
	@echo "  make restart  - Restart all services"
	@echo "  make logs     - Follow logs from all services"
	@echo "  make test     - Run backend tests"
	@echo "  make seed     - Populate database with 100k logs"
	@echo "  make migrate  - Run database migrations"
	@echo "  make clean    - Stop services and remove volumes"

start:
	docker-compose up -d
	@echo "Services started. Backend: http://localhost:8000, Frontend: http://localhost:3000"

stop:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

test:
	docker-compose exec backend pytest tests/ -v

seed:
	docker-compose exec backend python scripts/seed.py

migrate:
	docker-compose exec backend alembic upgrade head

clean:
	docker-compose down -v
	@echo "All services stopped and volumes removed"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| psycopg2 | psycopg3 (psycopg) | 2021-2022 | Native async support, no gevent/threading hacks needed with FastAPI |
| SQLAlchemy 1.x async | SQLAlchemy 2.0 async | 2023 | Mature async patterns with AsyncEngine, AsyncSession; no more bolted-on async |
| Black + Flake8 + isort | Ruff | 2023-2024 | 10-100x faster, single tool replaces three, used by FastAPI itself |
| Pydantic 1.x | Pydantic 2.x | 2023 | 5-50x performance improvement, required by FastAPI 0.100+ |
| Docker Compose v2 | Docker Compose v2 with conditional depends_on | 2020-2021 | service_healthy condition prevents race conditions on startup |
| Manual .env parsing | pydantic-settings | 2023 | Type-safe configuration with validation, PostgresDsn type support |
| timestamp without time zone | timestamptz (timestamp with time zone) | Always best practice | Prevents timezone-related bugs, stores UTC internally |

**Deprecated/outdated:**
- **psycopg2:** Legacy driver with no native async support; use psycopg3 (psycopg package)
- **SQLAlchemy 1.x:** Async support was bolted on; SQLAlchemy 2.0 has mature native async patterns
- **OFFSET pagination:** Performance degrades with large datasets; use cursor-based pagination (Phase 2)
- **Black + Flake8 + isort separately:** Ruff consolidates and accelerates all three tools
- **Wildcard CORS origins:** Blocks credential-based requests; always use explicit origin list

## Open Questions

1. **Should we use Alembic or raw SQL for initial schema creation?**
   - What we know: Alembic provides versioning, rollback, and autogenerate features
   - What's unclear: Whether the overhead of Alembic setup is justified for initial single migration
   - Recommendation: Use Alembic from the start. Even though Phase 1 only has one migration, Phase 2+ will need migrations for new tables/columns. Starting with Alembic establishes the pattern and avoids migration tool switching mid-project.

2. **What batch size should seed script use for optimal performance?**
   - What we know: SQLAlchemy bulk operations automatically batch, PostgreSQL COPY is fastest
   - What's unclear: Exact batch size for 100k logs to hit <60 second target
   - Recommendation: Start with SQLAlchemy bulk insert (simpler, still fast). If performance target isn't met, switch to PostgreSQL COPY with FREEZE option. Test with actual 100k dataset during Wave 0.

3. **Should BRIN index use default pages_per_range=128 or optimize further?**
   - What we know: BRIN indexes are much smaller than B-tree for sequential data
   - What's unclear: Whether 128 pages per range is optimal for our log ingestion pattern
   - Recommendation: Use default pages_per_range=128 with autosummarize=on. Can tune later based on actual query patterns in Phase 2+. Default is well-tested for time-series data.

4. **Should health check endpoint be included in OpenAPI docs?**
   - What we know: Health checks are typically consumed by monitoring tools, not humans
   - What's unclear: Whether to include in Swagger UI for visibility or hide with include_in_schema=False
   - Recommendation: Include in schema with clear documentation. Portfolio project benefits from showing thoughtful health check implementation. Production systems often use include_in_schema=False for monitoring endpoints.

## Sources

### Primary (HIGH confidence)
- [PostgreSQL 18 Documentation - TIMESTAMP types](https://www.postgresql.org/docs/current/datatype-datetime.html) - Timestamptz vs timestamp without time zone, UTC storage behavior
- [PostgreSQL 18 Documentation - CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html) - BRIN, B-tree, composite indexes, CONCURRENTLY option
- [PostgreSQL 18 Documentation - Multicolumn Indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html) - Column ordering, when to use composite indexes
- [PostgreSQL 18 Documentation - COPY command](https://www.postgresql.org/docs/current/sql-copy.html) - Bulk insert performance with COPY FROM STDIN, FREEZE option
- [FastAPI Documentation - CORS](https://fastapi.tiangolo.com/tutorial/cors/) - CORSMiddleware configuration, explicit origins vs wildcards
- [FastAPI Documentation - Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/) - HTTPException, custom exception handlers, validation errors
- [FastAPI Documentation - Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) - Project structure with routers, dependencies
- [SQLAlchemy 2.0 Documentation - Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) - AsyncEngine, AsyncSession, async_sessionmaker, expire_on_commit
- [SQLAlchemy 2.0 Documentation - Connection Pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html) - pool_size, max_overflow, pool_pre_ping, pool_recycle
- [SQLAlchemy 2.0 Documentation - Bulk Operations](https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html) - bulk_insert_mappings, insert() with execute()
- [Alembic Documentation - Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) - Migration setup, env.py configuration, async support
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - BaseSettings, .env file support, PostgresDsn validation
- [pytest Documentation - Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) - Fixture scopes, yield fixtures, cleanup patterns
- [Docker Compose Documentation - Services](https://docs.docker.com/compose/compose-file/05-services/) - Healthchecks, volume mounts, depends_on conditions
- [Docker Compose Documentation - Environment Variables](https://docs.docker.com/compose/environment-variables/set-environment-variables/) - .env file usage, env_file attribute

### Secondary (MEDIUM confidence)
- Existing project research: `.planning/research/STACK.md` - Technology stack decisions verified
- Existing project research: `.planning/research/PITFALLS.md` - Common pitfalls cross-referenced with official docs

### Tertiary (LOW confidence)
None - all findings verified with official documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All versions verified from official PyPI/npm sources or official documentation
- Architecture: HIGH - Patterns extracted directly from official FastAPI, SQLAlchemy, PostgreSQL, Docker Compose documentation
- Pitfalls: HIGH - All pitfalls cross-referenced with official documentation warnings and best practices
- Validation architecture: MEDIUM - Test framework patterns based on pytest docs, specific test coverage decisions are implementation choices

**Research date:** 2026-03-20
**Valid until:** 2026-04-20 (30 days - stack is stable, versions are current as of March 2026)
