---
phase: 02-core-api-layer
plan: 02
subsystem: core-api
tags: [api, crud, validation, testing]
dependency_graph:
  requires: [02-01-schemas-cursor]
  provides: [logs-create-endpoint, logs-read-endpoint]
  affects: [main-app-router-registration]
tech_stack:
  added: []
  patterns: [fastapi-router, async-crud, primary-key-lookup, http-404-handling]
key_files:
  created:
    - backend/app/routers/logs.py
    - backend/tests/test_logs_crud.py
  modified:
    - backend/app/main.py
    - backend/tests/conftest.py
decisions:
  - "Use db.get() for efficient primary key lookup instead of select() query"
  - "Return SQLAlchemy model directly from endpoints (Pydantic from_attributes handles conversion)"
  - "Status code 400 for all validation errors per Phase 1 exception handler convention"
  - "Created test database test_logs_db with same schema as development database"
metrics:
  duration_seconds: 351
  tasks_completed: 3
  files_created: 2
  files_modified: 2
  commits: 2
  tests_added: 15
  completed_at: "2026-03-21T06:47:00Z"
---

# Phase 02 Plan 02: POST and GET-by-ID Endpoints Summary

**One-liner:** REST endpoints for log creation (POST) and retrieval by ID (GET) with comprehensive validation and error handling

## What Was Built

Implemented two foundational CRUD endpoints for the Logs Dashboard API:

1. **POST /api/logs** - Create new log entries with full Pydantic validation
2. **GET /api/logs/{id}** - Retrieve single log by primary key with 404 handling

Both endpoints follow established Phase 1 patterns (async sessions, error handlers, router registration) and integrate seamlessly with Plan 02-01 schemas and utilities.

## Tasks Completed

### Task 1: POST /api/logs Endpoint (TDD)

**Commit:** `9ccf7af`

**Created:**
- `backend/app/routers/logs.py` - New router with POST endpoint accepting LogCreate schema
- `backend/tests/test_logs_crud.py` - 9 integration tests for create endpoint

**Modified:**
- `backend/app/main.py` - Registered logs router at /api prefix with "logs" tag
- `backend/tests/conftest.py` - Fixed test database password (blocking issue)

**Implementation:**
- Accepts LogCreate schema via request body (automatic Pydantic validation)
- Creates SQLAlchemy Log model instance from validated data
- Persists to database with `db.add()`, `db.commit()`, `db.refresh()`
- Returns 201 Created with full log object including server-generated id
- Validation errors return 400 with sanitized error details and request_id

**Tests (9 passing):**
- `test_create_log_success` - Valid POST returns 201 with created log
- `test_create_log_missing_timestamp` - Missing required field returns 400
- `test_create_log_missing_message` - Missing required field returns 400
- `test_create_log_timezone_naive` - Timezone-naive timestamp rejected with 400
- `test_create_log_invalid_severity` - Invalid severity enum rejected with 400
- `test_create_log_empty_message` - Empty string validation returns 400
- `test_create_log_empty_source` - Empty string validation returns 400
- `test_create_log_persisted` - Verifies log stored in database
- `test_create_log_all_severities` - All valid severities (INFO/WARNING/ERROR/CRITICAL) accepted

**Deviations:**
1. **Rule 3 - Blocking Issue:** Fixed test database password in conftest.py (was "changeme", needed "changeme_in_production" to match .env)
2. **Rule 1 - Bug Fix:** Fixed validation error handler in main.py to sanitize non-serializable error objects (ValueError instances in 'ctx' field caused JSON serialization errors)

### Task 2: GET /api/logs/{id} Endpoint (TDD)

**Commit:** `363490d`

**Modified:**
- `backend/app/routers/logs.py` - Added GET endpoint with primary key lookup
- `backend/tests/test_logs_crud.py` - Added 6 integration tests for get endpoint

**Implementation:**
- Path parameter `log_id: int` with automatic FastAPI validation
- Uses `db.get(Log, log_id)` for efficient primary key lookup
- Returns 200 OK with LogResponse for existing logs
- Returns 404 Not Found with detail message for non-existent ids
- Returns 400 for invalid id format (path validation)

**Tests (6 passing):**
- `test_get_log_by_id_success` - Valid GET returns 200 with log details
- `test_get_log_not_found` - Non-existent id returns 404
- `test_get_log_invalid_id` - Non-integer id returns 400 (path validation)
- `test_get_log_negative_id` - Negative id returns 404 (doesn't exist)
- `test_get_log_response_format` - Response contains exactly 5 fields
- `test_get_log_timezone_preserved` - Timestamp includes timezone indicator

### Task 3: Router Registration

**Status:** Completed in Task 1

Router registration in main.py was completed during Task 1 implementation:
```python
app.include_router(logs.router, prefix="/api", tags=["logs"])
```

Endpoints accessible at:
- POST `/api/logs`
- GET `/api/logs/{id}`

Both grouped under "logs" tag in OpenAPI documentation at `/docs`

## Test Results

**CRUD Tests:** 15/15 passing (100%)
- 9 create endpoint tests
- 6 get endpoint tests

**Overall Suite:** 34/38 passing (89%)
- ✅ 15 CRUD tests (this plan)
- ✅ 7 cursor utility tests (Plan 02-01)
- ✅ 9 schema validation tests (Plan 02-01)
- ✅ 3 health endpoint tests (Phase 1)
- ❌ 4 config tests (pre-existing failures, out of scope)

**Out of Scope:** The 4 failing config tests (`test_config.py`) existed before this plan and are unrelated to current changes. These test Phase 1's Settings class and fail due to Pydantic validation strictness changes. Per deviation rules, pre-existing failures in unrelated files are out of scope.

## Integration Points

**From Plan 02-01:**
- `LogCreate` schema for request validation
- `LogResponse` schema for response serialization
- Timezone validation from field_validator (rejects naive timestamps)
- Severity pattern validation (INFO|WARNING|ERROR|CRITICAL)

**From Phase 1:**
- `get_db()` dependency for async session injection
- `Log` SQLAlchemy model for database operations
- Exception handlers for validation (400) and server (500) errors
- Router registration pattern from health.py
- Test fixtures (client, test_db, test_engine) from conftest.py

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking Issue] Fixed test database password**
- **Found during:** Task 1 test execution
- **Issue:** conftest.py used hardcoded password "changeme" but actual password is "changeme_in_production" from .env
- **Fix:** Updated TEST_DATABASE_URL in conftest.py to use correct password
- **Files modified:** backend/tests/conftest.py
- **Commit:** 9ccf7af (included in Task 1 commit)

**2. [Rule 1 - Bug] Fixed validation error handler JSON serialization**
- **Found during:** Task 1 test execution (test_create_log_timezone_naive)
- **Issue:** Pydantic field validators include ValueError objects in error['ctx']['error'] which are not JSON serializable, causing server error 500 instead of validation error 400
- **Fix:** Added sanitization logic in validation_exception_handler to convert error objects to strings before JSON encoding
- **Files modified:** backend/app/main.py
- **Commit:** 9ccf7af (included in Task 1 commit)

**3. [Test Adjustment] Changed validation error status code from 422 to 400**
- **Found during:** Task 1 and Task 2 test execution
- **Issue:** Plan specified 422 for validation errors (FastAPI default), but Phase 1 established 400 via custom exception handler
- **Decision:** Follow existing convention from Phase 1 rather than introduce inconsistency
- **Files modified:** backend/tests/test_logs_crud.py (updated assertions in 8 tests)
- **Commits:** 9ccf7af, 363490d

## Files Changed

### Created (2 files, 363 lines)

**backend/app/routers/logs.py (80 lines)**
- FastAPI router with POST and GET endpoints
- POST /logs accepts LogCreate, returns 201 with LogResponse
- GET /logs/{log_id} returns 200 with LogResponse or 404
- Uses async/await for all database operations
- Comprehensive docstrings with Args/Returns/Raises sections

**backend/tests/test_logs_crud.py (283 lines)**
- 15 integration tests using pytest-asyncio
- 9 tests for POST endpoint (success + 8 validation cases)
- 6 tests for GET endpoint (success + error cases)
- Uses httpx AsyncClient from conftest.py fixtures
- Direct database verification for persistence test

### Modified (2 files)

**backend/app/main.py**
- Added `from .routers import logs` import
- Added `app.include_router(logs.router, prefix="/api", tags=["logs"])`
- Fixed validation_exception_handler to sanitize non-serializable error objects

**backend/tests/conftest.py**
- Updated TEST_DATABASE_URL password from "changeme" to "changeme_in_production"

## Verification

✅ **POST endpoint works:** Valid requests return 201 with created log, invalid requests return 400 with validation errors

✅ **GET endpoint works:** Existing ids return 200 with log details, non-existent ids return 404

✅ **Validation enforced:** Timezone-naive timestamps rejected, invalid severity values rejected, empty strings rejected

✅ **Database persistence:** Created logs stored in database and retrievable by id

✅ **Immutability respected:** No PUT/PATCH/DELETE endpoints exist (per LOG-05 requirement)

✅ **Test coverage:** 15 integration tests all passing (9 create + 6 get)

✅ **Router registered:** Endpoints accessible at /api/logs and /api/logs/{id}, visible in OpenAPI docs at /docs

✅ **Error handling:** Validation errors return 400 with request_id, server errors return 500 with request_id

✅ **Phase 1 patterns followed:** Async sessions, error handlers, router registration, test fixtures all reused correctly

## Technical Decisions

1. **Primary key lookup with db.get():** Used SQLAlchemy's `db.get(Model, pk)` method for GET endpoint instead of `select()` query. This is the most efficient way to fetch by primary key and returns None if not found (easy 404 handling).

2. **Direct model return from endpoints:** Return SQLAlchemy Log model instances directly from endpoint functions. Pydantic's `from_attributes=True` in LogResponse schema handles automatic conversion. This avoids manual field mapping and ensures consistency.

3. **Status code 400 for validation errors:** Followed Phase 1's established convention of returning 400 for validation errors rather than FastAPI's default 422. This maintains consistency across the API.

4. **Test database creation:** Created separate test_logs_db database to isolate test data from development data. Uses same schema via conftest.py fixtures that run migrations on test_engine.

5. **Error object sanitization:** When Pydantic field validators raise exceptions, those exception objects end up in error details and aren't JSON serializable. Added sanitization to convert these to strings before JSON encoding.

## Performance Notes

- **Execution time:** 351 seconds (5.85 minutes)
- **Database operations:** All async with proper session cleanup
- **Primary key lookups:** O(1) via index, most efficient query type
- **Test isolation:** Function-scoped fixtures ensure complete test isolation (create/drop tables per test)

## Next Steps

**Plan 02-03:** Implement GET /api/logs list endpoint with cursor-based pagination, filtering by date/severity/source, and sorting. Will reuse cursor utilities from Plan 02-01 and extend logs router with list endpoint.

**Integration ready:**
- LogListResponse schema already defined (Plan 02-01)
- Cursor encode/decode utilities tested and ready (Plan 02-01)
- Composite index on (timestamp, severity, source) exists (Phase 1)
- Router registration pattern established (this plan)

## Self-Check: PASSED

**Created files verified:**
```bash
✅ backend/app/routers/logs.py exists (80 lines)
✅ backend/tests/test_logs_crud.py exists (283 lines)
```

**Modified files verified:**
```bash
✅ backend/app/main.py contains logs router registration
✅ backend/tests/conftest.py contains updated password
```

**Commits verified:**
```bash
✅ 9ccf7af: feat(02-02): implement POST /api/logs endpoint with validation
✅ 363490d: feat(02-02): implement GET /api/logs/{id} endpoint
```

**Tests verified:**
```bash
✅ 15/15 CRUD tests passing
✅ All Phase 1 tests still passing (except pre-existing config failures)
```

**Endpoints verified:**
```bash
✅ POST /api/logs returns 201 with created log
✅ GET /api/logs/{id} returns 200 with log details
✅ Both endpoints visible in OpenAPI docs at /docs
```

All acceptance criteria met. Plan 02-02 complete.
