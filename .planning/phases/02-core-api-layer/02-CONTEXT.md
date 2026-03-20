# Phase 2: Core API Layer - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Complete REST API for log CRUD operations with cursor-based pagination, filtering by date range/severity/source, and sorting. This phase delivers:
- POST /api/logs - Create new log entries
- GET /api/logs - List logs with cursor pagination, filters, and sorting
- GET /api/logs/{id} - Retrieve single log details

No UI pages - those come in Phase 3. No CSV export - that's Phase 4. No analytics aggregations - that's Phase 5. This phase focuses purely on the core log management API endpoints.

</domain>

<decisions>
## Implementation Decisions

### API Response Structure
- **Paginated list format**: Envelope with metadata `{"data": [...], "next_cursor": "...", "has_more": true}`
- **Cursor format**: Base64-encoded {timestamp, id} tuple - opaque to clients, allows changing strategy later
- **GET /api/logs/{id}**: Same format as list items (consistent structure, reusable frontend types)
- **POST /api/logs response**: Full created log object with HTTP 201 (includes server-generated fields like id)
- **Empty results**: Consistent structure `{"data": [], "next_cursor": null, "has_more": false}`
- **Total count**: Not included - COUNT(\*) queries are expensive with 100k+ logs, cursor pagination doesn't need it
- **Timestamp format**: ISO 8601 with timezone (e.g., "2024-03-20T15:30:00Z") in all responses

### Filter Query Parameters
- **Date range**: Separate params `date_from` and `date_to` (allows open-ended ranges)
- **Severity filter**: Repeated params for multiple values (e.g., `severity=ERROR&severity=WARNING`)
- **Source filter**: Case-insensitive matching (ILIKE in SQL for better UX)
- **Sort**: Separate `sort` and `order` params (e.g., `sort=timestamp&order=desc`)
- **Supported sort fields**: timestamp, severity, source
- **Sort order values**: `asc` or `desc`

### Pagination Strategy Details
- **Default page size**: 50 items
- **Maximum page size**: 200 items (prevents abuse while allowing bulk operations)
- **Cursor location**: Response body field `next_cursor`
- **End of results**: `next_cursor = null` and `has_more = false` (explicit indicators)
- **Query parameter**: `cursor` for next page, `limit` for page size

### Validation and Error Cases
- **Timestamp input format**: ISO 8601 only (e.g., "2024-03-20T15:30:00Z")
- **Timezone-naive timestamps**: Reject with 400 error (require explicit timezone to prevent ambiguity)
- **Invalid cursor**: Return 400 with clear error message "Invalid cursor token"
- **Severity validation**: Strict validation - must be one of INFO, WARNING, ERROR, CRITICAL (reject with 400 otherwise)
- **Required fields for POST**: timestamp, message, severity, source (all required)
- **Message length**: No explicit limit mentioned - use database column limit (TEXT)
- **Source validation**: No strict validation - accept any non-empty string

### Claude's Discretion
- Exact pydantic model structure for request/response schemas
- Query optimization approach (use composite index from Phase 1)
- How to encode/decode base64 cursor (implementation details)
- Error message wording (as long as it's clear and follows Phase 1 patterns)
- Pydantic field validators for edge cases

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project requirements
- `.planning/PROJECT.md` - Project vision and constraints
- `.planning/REQUIREMENTS.md` - Requirements API-01 through API-06, LOG-01 through LOG-05
- `.planning/research/PITFALLS.md` - Critical pitfalls to avoid (cursor pagination, composite indexes)

### Prior phase context
- `.planning/phases/01-foundation-database/01-CONTEXT.md` - Error response format, validation patterns, established conventions

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **backend/app/models.py**: Log SQLAlchemy model with id, timestamp (timestamptz), message, severity, source columns
- **backend/app/database.py**: AsyncSessionLocal for database sessions, Base metadata
- **backend/app/dependencies.py**: get_db() async generator for FastAPI dependency injection
- **backend/app/config.py**: Settings class with pydantic-settings for environment config
- **backend/app/main.py**: FastAPI app with CORS, error handlers (validation 400, generic 500), request ID pattern
- **backend/tests/conftest.py**: test_db fixture, client fixture with dependency overrides

### Established Patterns
- **Async everywhere**: All database operations use async/await with SQLAlchemy 2.0
- **Error handling**: Custom exception handlers returning `{"detail": "message", "request_id": "uuid"}` format
- **Validation**: Pydantic models for request validation (FastAPI automatic)
- **Testing**: pytest with asyncio_mode="auto", function-scoped test fixtures
- **CORS**: Already configured in main.py with explicit origins

### Integration Points
- **Router registration**: Add new router to main.py with `app.include_router(logs_router, prefix="/api", tags=["logs"])`
- **Database access**: Use `Depends(get_db)` for async session injection
- **Test fixtures**: Use `client` fixture from conftest.py for endpoint testing

</code_context>

<specifics>
## Specific Ideas

- Cursor format being base64-encoded allows changing the pagination strategy later (e.g., adding secondary sort keys) without breaking clients
- Case-insensitive source filtering makes the API more user-friendly - users don't need to remember exact casing
- Rejecting timezone-naive timestamps forces proper timezone handling from the start, preventing bugs later
- Default 50-item page size is a sweet spot: not too many network round-trips, not too large payloads
- Strict severity validation ensures data quality and makes filtering reliable

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 02-core-api-layer*
*Context gathered: 2026-03-20*
