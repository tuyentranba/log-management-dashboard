# Phase 2: Core API Layer - Research

**Researched:** 2026-03-20
**Domain:** REST API development with FastAPI, cursor-based pagination, filtering, and sorting
**Confidence:** HIGH

## Summary

Phase 2 implements the complete REST API layer for log CRUD operations with cursor-based pagination, multi-criteria filtering, and sorting. The foundation from Phase 1 (database schema, FastAPI skeleton, test infrastructure) provides all necessary building blocks. This phase focuses on creating robust API endpoints with proper request/response validation, efficient query patterns, and comprehensive error handling.

The key technical challenge is implementing cursor-based pagination to avoid OFFSET performance degradation identified in PITFALLS.md. The solution uses base64-encoded cursor tokens containing (timestamp, id) tuples, enabling constant-time pagination regardless of page depth. Multi-value filtering (severity=ERROR&severity=WARNING) uses FastAPI's list query parameters, and all date handling enforces timezone awareness through Pydantic validation.

**Primary recommendation:** Build endpoints incrementally (POST → GET single → GET list with pagination → filters → sorting) with comprehensive test coverage at each step. Use existing patterns from Phase 1 (error handlers, validation, test fixtures) for consistency.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**API Response Structure:**
- Paginated list format: Envelope with metadata `{"data": [...], "next_cursor": "...", "has_more": true}`
- Cursor format: Base64-encoded {timestamp, id} tuple - opaque to clients, allows changing strategy later
- GET /api/logs/{id}: Same format as list items (consistent structure, reusable frontend types)
- POST /api/logs response: Full created log object with HTTP 201 (includes server-generated fields like id)
- Empty results: Consistent structure `{"data": [], "next_cursor": null, "has_more": false}`
- Total count: Not included - COUNT(*) queries are expensive with 100k+ logs, cursor pagination doesn't need it
- Timestamp format: ISO 8601 with timezone (e.g., "2024-03-20T15:30:00Z") in all responses

**Filter Query Parameters:**
- Date range: Separate params `date_from` and `date_to` (allows open-ended ranges)
- Severity filter: Repeated params for multiple values (e.g., `severity=ERROR&severity=WARNING`)
- Source filter: Case-insensitive matching (ILIKE in SQL for better UX)
- Sort: Separate `sort` and `order` params (e.g., `sort=timestamp&order=desc`)
- Supported sort fields: timestamp, severity, source
- Sort order values: `asc` or `desc`

**Pagination Strategy Details:**
- Default page size: 50 items
- Maximum page size: 200 items (prevents abuse while allowing bulk operations)
- Cursor location: Response body field `next_cursor`
- End of results: `next_cursor = null` and `has_more = false` (explicit indicators)
- Query parameter: `cursor` for next page, `limit` for page size

**Validation and Error Cases:**
- Timestamp input format: ISO 8601 only (e.g., "2024-03-20T15:30:00Z")
- Timezone-naive timestamps: Reject with 400 error (require explicit timezone to prevent ambiguity)
- Invalid cursor: Return 400 with clear error message "Invalid cursor token"
- Severity validation: Strict validation - must be one of INFO, WARNING, ERROR, CRITICAL (reject with 400 otherwise)
- Required fields for POST: timestamp, message, severity, source (all required)
- Message length: No explicit limit mentioned - use database column limit (TEXT)
- Source validation: No strict validation - accept any non-empty string

### Claude's Discretion

- Exact pydantic model structure for request/response schemas
- Query optimization approach (use composite index from Phase 1)
- How to encode/decode base64 cursor (implementation details)
- Error message wording (as long as it's clear and follows Phase 1 patterns)
- Pydantic field validators for edge cases

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| API-01 | REST API provides POST /api/logs endpoint to create logs | FastAPI POST endpoint with Pydantic request validation, SQLAlchemy async insert, return 201 with created object |
| API-02 | REST API provides GET /api/logs endpoint with pagination, filtering, sorting | FastAPI GET with Query parameters for cursor/limit/filters/sort, SQLAlchemy select with WHERE/ORDER BY, cursor encoding/decoding |
| API-03 | REST API provides GET /api/logs/{id} endpoint for single log detail | FastAPI path parameter validation, SQLAlchemy get by primary key, 404 handling |
| API-04 | REST API provides query endpoints with filtering by date range, severity, source | FastAPI list Query parameters for multiple severities, SQLAlchemy WHERE with date comparison and ILIKE for source |
| API-05 | REST API provides aggregated data endpoints for analytics | Deferred to Phase 5 (Analytics Dashboard) - not implemented in Phase 2 |
| API-06 | REST API provides CSV export endpoint | Deferred to Phase 4 (CSV Export) - not implemented in Phase 2 |
| LOG-01 | User can create new log entry with timestamp, message, severity, and source | Pydantic model validation for required fields, datetime with timezone, severity enum, non-empty strings |
| LOG-02 | User can view paginated list of all logs | Cursor pagination implementation, response envelope structure |
| LOG-03 | User can view detailed information for a single log | GET by ID endpoint, consistent response format |
| LOG-04 | Log list uses cursor-based pagination for constant query time | Base64 cursor with (timestamp, id), WHERE clause with > comparison using cursor values |
| LOG-05 | Logs are immutable (no edit or delete functionality) | No PUT/PATCH/DELETE endpoints - only POST and GET |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.135.1+ | REST API framework | Already installed in Phase 1, async-first, automatic OpenAPI docs, Pydantic integration |
| Pydantic | 2.x | Request/response validation | Bundled with FastAPI, v2 required for modern field validators, datetime timezone handling |
| SQLAlchemy | 2.0.48+ | Database ORM | Already installed in Phase 1, async support, robust query builder |
| httpx | 0.27+ | HTTP client for testing | Already used in conftest.py test fixtures, async support for FastAPI testing |
| pytest | 8.3+ | Testing framework | Already configured in Phase 1 with asyncio_mode='auto' |
| pytest-asyncio | 0.24+ | Async test support | Already installed, required for async endpoint tests |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-multipart | 0.0.20+ | Form data parsing | If adding file upload support (not needed for Phase 2) |
| email-validator | 2.2+ | Email validation | If validating email fields (not needed for Phase 2) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Cursor pagination | OFFSET/LIMIT | OFFSET is simple but degrades at scale - PITFALLS.md shows 10-100x slowdown at page 100+ |
| Pydantic field validators | Manual validation | Field validators are declarative, testable, and auto-documented in OpenAPI |
| Base64 cursor | Integer cursor | Base64 allows encoding multiple fields, provides opacity, future-proof for strategy changes |
| FastAPI Query | Manual query parsing | Query provides automatic validation, OpenAPI documentation, type coercion |

**Installation:**
All dependencies already installed in Phase 1 requirements.txt. No additional packages needed for Phase 2.

## Architecture Patterns

### Recommended Project Structure
```
backend/app/
├── routers/
│   ├── health.py         # Existing from Phase 1
│   └── logs.py           # NEW: Log CRUD endpoints
├── schemas/
│   └── logs.py           # NEW: Pydantic request/response models
├── models.py             # Existing: SQLAlchemy Log model
├── dependencies.py       # Existing: get_db dependency
├── database.py           # Existing: Async session
├── config.py             # Existing: Settings
└── main.py               # Existing: FastAPI app - add logs router

backend/tests/
├── conftest.py           # Existing: Test fixtures
├── test_health.py        # Existing from Phase 1
└── test_logs.py          # NEW: Log endpoint tests
```

### Pattern 1: Pydantic Schema Separation
**What:** Separate request schemas from response schemas even when fields overlap
**When to use:** Always for POST endpoints, optional for GET if response adds server-generated fields
**Example:**
```python
# Source: FastAPI best practices + Phase 1 established patterns
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LogCreate(BaseModel):
    """Request schema for creating logs."""
    timestamp: datetime  # Pydantic validates timezone awareness
    message: str = Field(min_length=1)
    severity: str = Field(pattern="^(INFO|WARNING|ERROR|CRITICAL)$")
    source: str = Field(min_length=1, max_length=100)

class LogResponse(BaseModel):
    """Response schema for log objects."""
    id: int
    timestamp: datetime
    message: str
    severity: str
    source: str

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy

class LogListResponse(BaseModel):
    """Response envelope for paginated list."""
    data: list[LogResponse]
    next_cursor: Optional[str]
    has_more: bool
```

### Pattern 2: Cursor Encoding/Decoding
**What:** Base64-encode cursor values to make them opaque and future-proof
**When to use:** All pagination cursors to prevent client assumptions about format
**Example:**
```python
# Source: Common API pagination pattern + CONTEXT.md specification
import base64
import json
from typing import Optional

def encode_cursor(timestamp: datetime, log_id: int) -> str:
    """Encode pagination cursor as base64."""
    cursor_data = {
        "timestamp": timestamp.isoformat(),
        "id": log_id
    }
    json_str = json.dumps(cursor_data)
    return base64.b64encode(json_str.encode()).decode()

def decode_cursor(cursor: str) -> tuple[datetime, int]:
    """Decode pagination cursor from base64."""
    try:
        json_str = base64.b64decode(cursor.encode()).decode()
        cursor_data = json.loads(json_str)
        return (
            datetime.fromisoformat(cursor_data["timestamp"]),
            cursor_data["id"]
        )
    except (ValueError, KeyError, json.JSONDecodeError):
        raise ValueError("Invalid cursor token")
```

### Pattern 3: Cursor-Based Query Construction
**What:** Use WHERE clauses with cursor values instead of OFFSET for pagination
**When to use:** All paginated list endpoints to maintain constant query time
**Example:**
```python
# Source: PITFALLS.md Pitfall 1 + PostgreSQL keyset pagination pattern
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

async def get_logs_paginated(
    session: AsyncSession,
    cursor: Optional[str] = None,
    limit: int = 50
) -> tuple[list[Log], Optional[str], bool]:
    """
    Get paginated logs using cursor-based pagination.

    Cursor encodes (timestamp, id) for stable ordering.
    Returns (logs, next_cursor, has_more).
    """
    query = select(Log).order_by(Log.timestamp.desc(), Log.id.desc())

    # Apply cursor filter if provided
    if cursor:
        cursor_ts, cursor_id = decode_cursor(cursor)
        # Use composite comparison: timestamp < cursor OR (timestamp = cursor AND id < cursor_id)
        query = query.where(
            or_(
                Log.timestamp < cursor_ts,
                and_(Log.timestamp == cursor_ts, Log.id < cursor_id)
            )
        )

    # Fetch limit + 1 to determine if more pages exist
    query = query.limit(limit + 1)
    result = await session.execute(query)
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

    return logs, next_cursor, has_more
```

### Pattern 4: Multi-Value Query Parameter Filtering
**What:** Accept repeated query parameters for multi-value filters like severity
**When to use:** When users need to filter by multiple values of the same field
**Example:**
```python
# Source: FastAPI Query parameters documentation + CONTEXT.md specification
from typing import Annotated, Optional
from fastapi import Query

@router.get("/logs")
async def list_logs(
    severity: Annotated[list[str] | None, Query()] = None,
    source: Annotated[str | None, Query()] = None,
    date_from: Annotated[datetime | None, Query()] = None,
    date_to: Annotated[datetime | None, Query()] = None,
    sort: Annotated[str, Query(pattern="^(timestamp|severity|source)$")] = "timestamp",
    order: Annotated[str, Query(pattern="^(asc|desc)$")] = "desc",
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    List logs with pagination, filtering, and sorting.

    URL example: /logs?severity=ERROR&severity=WARNING&source=api&limit=50
    """
    # Build query with filters
    query = select(Log)

    if severity:
        query = query.where(Log.severity.in_(severity))

    if source:
        query = query.where(Log.source.ilike(f"%{source}%"))

    if date_from:
        query = query.where(Log.timestamp >= date_from)

    if date_to:
        query = query.where(Log.timestamp <= date_to)

    # Apply sorting
    sort_column = getattr(Log, sort)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Execute with pagination
    # ... (use cursor pagination pattern from Pattern 3)
```

### Pattern 5: Timezone-Aware Datetime Validation
**What:** Use Pydantic field validators to reject timezone-naive timestamps
**When to use:** All datetime input fields to prevent timezone bugs (PITFALLS.md Pitfall 3)
**Example:**
```python
# Source: Pydantic field validators + PITFALLS.md Pitfall 3
from pydantic import BaseModel, field_validator
from datetime import datetime

class LogCreate(BaseModel):
    timestamp: datetime
    message: str
    severity: str
    source: str

    @field_validator('timestamp')
    @classmethod
    def validate_timezone_aware(cls, v: datetime) -> datetime:
        """Ensure timestamp includes timezone information."""
        if v.tzinfo is None:
            raise ValueError(
                "Timestamp must include timezone. "
                "Use ISO 8601 format: 2024-03-20T15:30:00Z"
            )
        return v
```

### Anti-Patterns to Avoid

- **Using OFFSET for pagination:** Degrades to multi-second queries at page 100+ with 100k logs (PITFALLS.md Pitfall 1)
- **Loading all logs then filtering in Python:** Defeats database indexing, causes memory issues (PITFALLS.md Pitfall 4)
- **Including total count in list responses:** COUNT(*) requires full table scan, adds 100ms+ to every request (PITFALLS.md Pitfall 5)
- **Accepting timezone-naive timestamps:** Creates inconsistent data across DST boundaries (PITFALLS.md Pitfall 3)
- **Using wildcards in CORS with credentials:** Blocks authentication headers (PITFALLS.md Pitfall 7) - already handled in Phase 1
- **Not validating cursor tokens:** Exposes implementation details, allows invalid queries that crash server

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Request validation | Manual type checking, try/except | Pydantic models with Field validators | Pydantic handles type coercion, validation, error messages, OpenAPI docs automatically |
| Cursor encoding | Plain text timestamp or ID | base64 JSON encoding | Base64 makes cursors opaque, prevents client assumptions, allows adding fields without breaking changes |
| Query parameter parsing | request.query_params dict | FastAPI Query with Annotated | Query provides automatic type coercion, validation, list handling, OpenAPI docs |
| Datetime timezone handling | Manual timezone conversion | Pydantic datetime + field validator | Handles ISO 8601 parsing, timezone validation, prevents naive datetime bugs |
| Response serialization | dict() or to_dict() methods | Pydantic response models with from_attributes | Automatic ORM conversion, consistent format, type safety, OpenAPI schema generation |
| Filter validation | if/else chains | Pydantic Query with regex patterns | Declarative, testable, auto-documented, prevents invalid filter values |
| Error responses | Custom error dicts | FastAPI exception handlers | Already configured in Phase 1, consistent format with request_id |

**Key insight:** FastAPI + Pydantic handle 90% of REST API boilerplate automatically. Custom code should focus on business logic (query construction, cursor encoding) not validation/serialization plumbing.

## Common Pitfalls

### Pitfall 1: Cursor Pagination Edge Cases
**What goes wrong:** Cursor pagination breaks when sorting by non-unique columns or when cursor items are deleted
**Why it happens:** Single-field cursors (just timestamp) cause duplicates when multiple logs share same timestamp. If cursor log is deleted, pagination skips the next page.
**How to avoid:** Always include primary key (id) as secondary sort field. Encode both timestamp and id in cursor. Use composite comparison in WHERE clause: `(timestamp, id) < (cursor_timestamp, cursor_id)` for stable ordering.
**Warning signs:** Duplicate logs across pages, missing logs between pages, inconsistent results when re-fetching same page

### Pitfall 2: Severity Filter SQL Injection via IN Clause
**What goes wrong:** Building SQL IN clause with string concatenation creates SQL injection vulnerability
**Why it happens:** Developer constructs `WHERE severity IN ('ERROR', 'WARNING')` by string joining user input
**How to avoid:** Use SQLAlchemy's `.in_()` method which handles parameterization: `Log.severity.in_(severity_list)`. FastAPI Query validation ensures severity values are from allowed enum before reaching database.
**Warning signs:** Direct string concatenation in queries, query strings containing user input, linter warnings about SQL injection

### Pitfall 3: ILIKE Performance Degradation
**What goes wrong:** Case-insensitive source filtering with ILIKE bypasses indexes, causing full table scans
**Why it happens:** PostgreSQL can't use B-tree indexes for ILIKE queries, requires sequential scan through all rows
**How to avoid:** For Phase 2, accept the performance hit (source filtering is optional, users can avoid it). For production, consider: (1) Store lowercase source in separate indexed column, (2) Use PostgreSQL trigram indexes (pg_trgm), (3) Switch to full-text search for source field. Document limitation in Phase 2 acceptance criteria.
**Warning signs:** EXPLAIN ANALYZE shows "Seq Scan" on logs table when source filter applied, query time increases linearly with log count

### Pitfall 4: Base64 Cursor Encoding Without Error Handling
**What goes wrong:** Invalid cursor tokens crash the API with 500 errors instead of returning meaningful 400 errors
**Why it happens:** decode_cursor() raises generic exceptions (ValueError, json.JSONDecodeError) that aren't caught
**How to avoid:** Wrap all cursor decoding in try/except that raises FastAPI HTTPException with 400 status and clear message "Invalid cursor token". Validate cursor structure after decoding (has timestamp and id fields).
**Warning signs:** 500 errors for malformed cursors in logs, missing error handling in decode_cursor function, no tests for invalid cursor formats

### Pitfall 5: Missing Limit Validation Allows Resource Exhaustion
**What goes wrong:** User requests limit=999999, API tries to load millions of logs into memory, crashes with OOM
**Why it happens:** No maximum validation on limit parameter, attacker can abuse pagination
**How to avoid:** Use FastAPI Query with `le=200` constraint per CONTEXT.md specification. Validate at API layer before reaching database.
**Warning signs:** Memory spikes on pagination requests, missing max validation in Query parameter, no tests for limit boundary cases

### Pitfall 6: Timezone Loss in Response Serialization
**What goes wrong:** Database stores timestamptz, but response JSON shows naive timestamps without timezone suffix
**Why it happens:** Python datetime to JSON serialization drops timezone info unless explicitly formatted
**How to avoid:** Pydantic automatically preserves timezone in JSON serialization when using datetime fields. Verify responses include timezone (e.g., "2024-03-20T15:30:00+00:00" or "2024-03-20T15:30:00Z"). Test with assertions checking for timezone in response data.
**Warning signs:** Response timestamps missing 'Z' or '+00:00' suffix, frontend showing wrong times, tests not checking timezone format

## Code Examples

Verified patterns from official sources:

### Creating Log Entry
```python
# Source: FastAPI POST endpoint pattern + SQLAlchemy async insert
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.models import Log
from app.schemas.logs import LogCreate, LogResponse

router = APIRouter()

@router.post("/logs", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(
    log_data: LogCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new log entry.

    Returns the created log with server-generated id.
    """
    # Create SQLAlchemy model instance
    log = Log(
        timestamp=log_data.timestamp,
        message=log_data.message,
        severity=log_data.severity,
        source=log_data.source
    )

    # Add to session and commit
    db.add(log)
    await db.commit()
    await db.refresh(log)  # Load server-generated id

    return log
```

### Getting Single Log by ID
```python
# Source: FastAPI path parameter + SQLAlchemy get by primary key
from fastapi import HTTPException

@router.get("/logs/{log_id}", response_model=LogResponse)
async def get_log(
    log_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single log by ID.

    Returns 404 if log not found.
    """
    log = await db.get(Log, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log with id {log_id} not found"
        )
    return log
```

### List Logs with Filtering and Sorting
```python
# Source: Combining Patterns 3 (cursor pagination) + Pattern 4 (multi-value filters)
from sqlalchemy import select, and_, or_

@router.get("/logs", response_model=LogListResponse)
async def list_logs(
    severity: Annotated[list[str] | None, Query()] = None,
    source: Annotated[str | None, Query()] = None,
    date_from: Annotated[datetime | None, Query()] = None,
    date_to: Annotated[datetime | None, Query()] = None,
    sort: Annotated[str, Query(pattern="^(timestamp|severity|source)$")] = "timestamp",
    order: Annotated[str, Query(pattern="^(asc|desc)$")] = "desc",
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    List logs with cursor-based pagination, filtering, and sorting.

    Filters can be combined - results match ALL criteria (AND logic).
    Multiple severity values use OR logic (match any).
    """
    # Start with base query
    query = select(Log)

    # Apply filters
    if severity:
        # Validate severity values
        valid_severities = {"INFO", "WARNING", "ERROR", "CRITICAL"}
        for sev in severity:
            if sev not in valid_severities:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid severity: {sev}. Must be one of: {', '.join(valid_severities)}"
                )
        query = query.where(Log.severity.in_(severity))

    if source:
        query = query.where(Log.source.ilike(f"%{source}%"))

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

    # Always include id as secondary sort for stable ordering
    query = query.order_by(sort_direction, Log.id.desc() if order == "desc" else Log.id.asc())

    # Apply cursor pagination
    if cursor:
        try:
            cursor_ts, cursor_id = decode_cursor(cursor)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Composite cursor comparison based on sort direction
        if order == "desc":
            query = query.where(
                or_(
                    sort_column < cursor_ts,
                    and_(sort_column == cursor_ts, Log.id < cursor_id)
                )
            )
        else:
            query = query.where(
                or_(
                    sort_column > cursor_ts,
                    and_(sort_column == cursor_ts, Log.id > cursor_id)
                )
            )

    # Fetch limit + 1 to check for more pages
    query = query.limit(limit + 1)
    result = await db.execute(query)
    logs = list(result.scalars().all())

    # Determine if more pages exist
    has_more = len(logs) > limit
    if has_more:
        logs = logs[:limit]

    # Generate next cursor
    next_cursor = None
    if has_more and logs:
        last_log = logs[-1]
        next_cursor = encode_cursor(last_log.timestamp, last_log.id)

    return LogListResponse(
        data=logs,
        next_cursor=next_cursor,
        has_more=has_more
    )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| OFFSET/LIMIT pagination | Cursor/keyset pagination | ~2015 | Constant query time regardless of page depth, required for 100k+ datasets |
| Pydantic v1 @validator | Pydantic v2 @field_validator | 2023 | Clearer syntax, better performance, required for FastAPI 0.100+ |
| SQLAlchemy 1.4 Query API | SQLAlchemy 2.0 select() API | 2023 | Type safety, async-first, simpler query construction |
| Manual Query validation | FastAPI Query with Annotated | 2023 (FastAPI 0.95+) | Better IDE support, explicit typing, recommended by docs |
| pytest-asyncio explicit decorator | asyncio_mode='auto' | 2022 | No @pytest.mark.asyncio needed, cleaner test code |

**Deprecated/outdated:**
- Query parameters as default values without Annotated: Still works but not recommended, IDE support limited
- Pydantic v1 Config.orm_mode: Renamed to from_attributes in v2, old name deprecated
- SQLAlchemy Query.filter(): Replaced by select().where() in 2.0, more consistent with SQL

## Open Questions

1. **Should cursor pagination support bidirectional navigation (previous page)?**
   - What we know: Current spec only requires forward pagination with next_cursor
   - What's unclear: Whether users will want "previous page" functionality in UI
   - Recommendation: Start with forward-only (simpler), add reverse cursors in Phase 3 if UI needs it. Reverse requires encoding direction in cursor and reversing sort order.

2. **How to handle cursor invalidation when underlying data changes?**
   - What we know: If cursor log is deleted, pagination continues correctly (uses composite comparison)
   - What's unclear: Whether to detect/warn when cursor is very old (hours/days) and dataset has changed significantly
   - Recommendation: Accept that cursors show point-in-time snapshots, don't try to detect staleness. Document behavior: cursors remain valid but may skip/duplicate items if data changes between pages.

3. **Should source ILIKE filter use index optimization now or defer?**
   - What we know: ILIKE bypasses indexes, causes seq scans (acceptable for MVP, optional filter)
   - What's unclear: Whether performance will be acceptable in practice or needs immediate optimization
   - Recommendation: Ship with ILIKE in Phase 2, measure performance in Phase 6 testing, optimize only if Phase 3 performance tests fail. Optimization options: trigram index, lowercase column, full-text search.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.3+ with pytest-asyncio 0.24+ |
| Config file | backend/pyproject.toml (already configured in Phase 1) |
| Quick run command | `make test -k "test_logs"` |
| Full suite command | `make test` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| API-01 | POST /api/logs creates log with 201 | integration | `pytest tests/test_logs.py::test_create_log -x` | ❌ Wave 0 |
| API-01 | POST rejects missing required fields | integration | `pytest tests/test_logs.py::test_create_log_missing_fields -x` | ❌ Wave 0 |
| API-01 | POST rejects invalid severity | integration | `pytest tests/test_logs.py::test_create_log_invalid_severity -x` | ❌ Wave 0 |
| API-01 | POST rejects timezone-naive timestamp | integration | `pytest tests/test_logs.py::test_create_log_no_timezone -x` | ❌ Wave 0 |
| API-02 | GET /api/logs returns paginated results | integration | `pytest tests/test_logs.py::test_list_logs_pagination -x` | ❌ Wave 0 |
| API-02 | GET respects limit parameter | integration | `pytest tests/test_logs.py::test_list_logs_limit -x` | ❌ Wave 0 |
| API-02 | GET rejects limit > 200 | integration | `pytest tests/test_logs.py::test_list_logs_limit_exceeded -x` | ❌ Wave 0 |
| API-02 | GET returns next_cursor when more pages exist | integration | `pytest tests/test_logs.py::test_list_logs_cursor -x` | ❌ Wave 0 |
| API-02 | GET with cursor returns next page | integration | `pytest tests/test_logs.py::test_list_logs_cursor_pagination -x` | ❌ Wave 0 |
| API-02 | GET rejects invalid cursor format | integration | `pytest tests/test_logs.py::test_list_logs_invalid_cursor -x` | ❌ Wave 0 |
| API-03 | GET /api/logs/{id} returns log details | integration | `pytest tests/test_logs.py::test_get_log_by_id -x` | ❌ Wave 0 |
| API-03 | GET /api/logs/{id} returns 404 if not found | integration | `pytest tests/test_logs.py::test_get_log_not_found -x` | ❌ Wave 0 |
| API-04 | GET filters by single severity | integration | `pytest tests/test_logs.py::test_filter_by_severity -x` | ❌ Wave 0 |
| API-04 | GET filters by multiple severities | integration | `pytest tests/test_logs.py::test_filter_by_multiple_severities -x` | ❌ Wave 0 |
| API-04 | GET filters by source (case-insensitive) | integration | `pytest tests/test_logs.py::test_filter_by_source -x` | ❌ Wave 0 |
| API-04 | GET filters by date_from | integration | `pytest tests/test_logs.py::test_filter_by_date_from -x` | ❌ Wave 0 |
| API-04 | GET filters by date_to | integration | `pytest tests/test_logs.py::test_filter_by_date_to -x` | ❌ Wave 0 |
| API-04 | GET filters by date range | integration | `pytest tests/test_logs.py::test_filter_by_date_range -x` | ❌ Wave 0 |
| API-04 | GET combines multiple filters (AND) | integration | `pytest tests/test_logs.py::test_filter_combined -x` | ❌ Wave 0 |
| LOG-04 | Cursor pagination maintains consistent boundaries | integration | `pytest tests/test_logs.py::test_pagination_consistency -x` | ❌ Wave 0 |
| LOG-04 | Pagination performance with 100k logs | integration | `pytest tests/test_logs.py::test_pagination_performance -x --slow` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `make test -k "test_logs"` (run all log endpoint tests)
- **Per wave merge:** `make test` (full test suite including Phase 1 tests)
- **Phase gate:** Full suite green + performance test passing (<500ms for page 100+) before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_logs.py` — covers all API-01, API-02, API-03, API-04, LOG-04 requirements
- [ ] `app/routers/logs.py` — log CRUD endpoints
- [ ] `app/schemas/logs.py` — Pydantic request/response models

Performance test (test_pagination_performance) requires 100k logs in test database. Can use seed script from Phase 1 or create helper fixture that generates test data efficiently.

## Sources

### Primary (HIGH confidence)
- FastAPI Query Parameters: https://fastapi.tiangolo.com/tutorial/query-params/ - Query parameter basics
- FastAPI Query Validation: https://fastapi.tiangolo.com/tutorial/query-params-str-validations/ - Query with Annotated, list parameters
- FastAPI Body Fields: https://fastapi.tiangolo.com/tutorial/body-fields/ - Field validation patterns
- FastAPI Custom Responses: https://fastapi.tiangolo.com/advanced/custom-response/ - StreamingResponse for CSV
- Pydantic Models: https://docs.pydantic.dev/latest/concepts/models/ - Model validation, datetime handling
- Pydantic Validators: https://docs.pydantic.dev/latest/api/functional_validators/ - Field validators
- SQLAlchemy Select: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html - Query construction, filtering
- PostgreSQL LIMIT/OFFSET: https://www.postgresql.org/docs/current/queries-limit.html - Performance characteristics
- Phase 1 CONTEXT.md: Established error handling, validation patterns, test infrastructure
- PITFALLS.md: Cursor pagination (Pitfall 1), composite indexes (Pitfall 2), timezone handling (Pitfall 3)

### Secondary (MEDIUM confidence)
- Existing codebase Phase 1: models.py (Log model with timestamptz), main.py (error handlers, CORS), dependencies.py (get_db), conftest.py (test fixtures)

### Tertiary (LOW confidence)
- None - all findings verified with official documentation or existing codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already installed in Phase 1, versions verified in requirements.txt
- Architecture: HIGH - Patterns derived from official documentation and PITFALLS.md analysis
- Pitfalls: HIGH - Direct citations from PITFALLS.md with official PostgreSQL/FastAPI documentation support
- Code examples: HIGH - Based on official FastAPI/SQLAlchemy documentation patterns adapted to project needs
- Testing: HIGH - Test infrastructure exists from Phase 1, test patterns established

**Research date:** 2026-03-20
**Valid until:** 2026-04-20 (30 days - FastAPI/SQLAlchemy stable, minor version updates expected but no breaking changes)
