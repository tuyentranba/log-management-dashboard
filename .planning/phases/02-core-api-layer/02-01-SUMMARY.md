---
phase: 02-core-api-layer
plan: 01
subsystem: core-api
tags:
  - pydantic
  - schemas
  - cursor-pagination
  - validation
  - testing
dependency_graph:
  requires: []
  provides:
    - cursor-utilities
    - log-schemas
    - timezone-validation
  affects: []
tech_stack:
  added:
    - pydantic-field-validators
    - base64-cursor-encoding
  patterns:
    - timezone-aware-validation
    - orm-compatibility
    - cursor-based-pagination
key_files:
  created:
    - backend/app/utils/cursor.py
    - backend/app/utils/__init__.py
    - backend/app/schemas/logs.py
    - backend/app/schemas/__init__.py
    - backend/tests/test_cursor.py
    - backend/tests/test_schemas.py
  modified:
    - backend/Dockerfile
    - backend/requirements.txt
decisions:
  - id: cursor-base64-encoding
    summary: Use base64-encoded JSON for cursor tokens
    rationale: Opaque format allows changing pagination strategy without breaking clients
    alternatives: Plain text timestamp+id, encrypted tokens
    outcome: Base64 provides opacity and flexibility without encryption overhead
  - id: timezone-validation
    summary: Reject timezone-naive timestamps at schema level
    rationale: Prevents ambiguity and timezone bugs throughout application
    alternatives: Auto-assume UTC, accept naive timestamps
    outcome: Explicit validation enforces correctness from the start
  - id: severity-pattern-validation
    summary: Use Pydantic pattern field for severity validation
    rationale: Simple regex validation, clear error messages
    alternatives: Enum type, custom validator
    outcome: Pattern validation is concise and provides clear validation errors
metrics:
  duration: 2950
  tasks_completed: 2
  tests_added: 16
  lines_added: 490
  completed_date: "2026-03-20"
---

# Phase 02 Plan 01: Pydantic Schemas and Cursor Utilities Summary

**One-liner:** Created base64-encoded cursor pagination utilities and Pydantic schemas with timezone-aware validation for log CRUD operations.

## What Was Built

### Cursor Pagination Utilities
- **encode_cursor()**: Converts timestamp+id to opaque base64 token
- **decode_cursor()**: Parses base64 token with comprehensive error handling
- **Error validation**: Rejects invalid base64, malformed JSON, missing fields
- **Opacity**: Base64 encoding prevents clients from reading internal data

### Pydantic Schemas
- **LogCreate**: Request schema with timezone validation and severity enum
  - Timezone validator rejects naive datetime (tzinfo is None)
  - Pattern validation for severity: INFO|WARNING|ERROR|CRITICAL
  - min_length=1 for message and source fields
- **LogResponse**: Response schema with ORM compatibility
  - from_attributes=True enables SQLAlchemy model validation
  - Preserves timezone in JSON serialization
- **LogListResponse**: Paginated response envelope
  - data array, next_cursor (nullable), has_more boolean

## Test Coverage

**16 unit tests total (all passing):**

**Cursor tests (7):**
- encode_cursor produces valid base64 with timestamp+id JSON
- decode_cursor reconstructs original values
- Invalid base64 raises ValueError("Invalid cursor token")
- Invalid JSON raises ValueError("Invalid cursor token")
- Missing fields raise ValueError("Invalid cursor token")
- Encode/decode roundtrip preserves exact values
- Encoded cursor is opaque (no readable timestamp/id)

**Schema tests (9):**
- LogCreate validates with timezone-aware timestamp
- LogCreate rejects timezone-naive timestamps
- LogCreate rejects invalid severity values
- LogCreate accepts all valid severities (INFO, WARNING, ERROR, CRITICAL)
- LogCreate rejects empty message (min_length=1)
- LogCreate rejects empty source (min_length=1)
- LogResponse.model_validate() works with SQLAlchemy Log instances
- LogListResponse structure validates correctly
- LogResponse preserves timezone in JSON output (Z or +00:00)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking Issue] Fixed psycopg binary module missing**
- **Found during:** Task 1 setup
- **Issue:** Backend container failing to start with "ImportError: no pq wrapper available"
- **Fix:** Changed `psycopg==3.3.3` to `psycopg[binary]==3.3.3` in requirements.txt
- **Files modified:** backend/requirements.txt
- **Commit:** f072e67 (included with Task 1)

**2. [Rule 3 - Blocking Issue] Added dev dependencies to Docker image**
- **Found during:** Task 1 test execution
- **Issue:** pytest not installed in backend container, blocking test execution
- **Fix:** Modified Dockerfile to install requirements-dev.txt
- **Files modified:** backend/Dockerfile
- **Commit:** f072e67 (included with Task 1)

Both fixes were necessary to unblock task execution. The psycopg binary issue prevented the backend from starting, and missing pytest prevented test execution. These are infrastructure fixes, not code bugs.

## Integration Points

**With Phase 1:**
- Cursor utilities use datetime from Python stdlib (consistent with Phase 1 models)
- LogResponse.model_validate() works with SQLAlchemy Log model from Plan 01-01
- Test patterns follow conftest.py fixtures from Plan 01-05
- Severity values match seed script from Plan 01-04

**For Future Plans:**
- Plan 02-02 (log ingestion endpoint) will use LogCreate for request validation
- Plan 02-03 (log list endpoint) will use encode_cursor/decode_cursor for pagination
- Plan 02-03 will use LogListResponse for paginated responses

## Self-Check: PASSED

**Created files exist:**
```
FOUND: backend/app/utils/__init__.py
FOUND: backend/app/utils/cursor.py
FOUND: backend/app/schemas/__init__.py
FOUND: backend/app/schemas/logs.py
FOUND: backend/tests/test_cursor.py
FOUND: backend/tests/test_schemas.py
```

**Commits exist:**
```
FOUND: f072e67 (Task 1: cursor utilities)
FOUND: 0dd78f7 (Task 2: Pydantic schemas)
```

**Tests pass:**
```
16/16 tests passing (7 cursor + 9 schema)
```

All artifacts delivered as planned.

## Key Learnings

1. **Base64 cursor encoding** provides good balance of opacity and simplicity - no encryption needed for non-sensitive pagination data
2. **Pydantic field validators** are powerful for enforcing domain rules (timezone awareness) at the schema boundary
3. **ORM compatibility** with from_attributes=True makes response schemas reusable across endpoints
4. **Docker dev dependencies** should be installed in development images to enable in-container testing

## Next Steps

Plan 02-02 will implement the POST /api/logs endpoint using LogCreate schema for validation and LogResponse for responses. Plan 02-03 will implement GET /api/logs with cursor pagination using encode_cursor/decode_cursor utilities.

---

**Execution time:** 2950 seconds (49.2 minutes)
**Tasks:** 2/2 completed
**Tests:** 16 passed
**Status:** ✅ Complete
