---
phase: 01
slug: foundation-database
status: ready
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-20
updated: 2026-03-20
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 with pytest-asyncio 1.3.0 |
| **Config file** | backend/pyproject.toml |
| **Quick run command** | `pytest tests/test_health.py -x` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds (quick), ~20 seconds (full) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_health.py -x` (quick smoke test)
- **After every plan wave:** Run `pytest tests/ -v` (full suite)
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-1 | 01 | 1 | DB-01, DB-02 | integration | `test -f backend/requirements.txt && grep -q "sqlalchemy==2.0.48" backend/requirements.txt && test -f backend/app/models.py && grep -q "TIMESTAMP(timezone=True)" backend/app/models.py && test -f backend/app/database.py && grep -q "expire_on_commit=False" backend/app/database.py` | ✅ | ⬜ pending |
| 01-01-2 | 01 | 1 | DB-03, DB-04, DB-05 | integration | `test -f backend/alembic.ini && test -f backend/alembic/env.py && grep -q "from app.models import Base" backend/alembic/env.py && grep -q "asyncio.run" backend/alembic/env.py` | ✅ | ⬜ pending |
| 01-01-3 | 01 | 1 | DB-03, DB-04, DB-05 | integration | `test -f backend/alembic/versions/001_create_logs_table.py && grep -q "idx_logs_timestamp_brin" backend/alembic/versions/001_create_logs_table.py && grep -q "idx_logs_composite" backend/alembic/versions/001_create_logs_table.py` | ✅ | ⬜ pending |
| 01-02-1 | 02 | 1 | INFRA-01, INFRA-02 | integration | `test -f docker-compose.yml && grep -q "postgres:" docker-compose.yml && grep -q "backend:" docker-compose.yml && grep -q "frontend:" docker-compose.yml && grep -q "service_healthy" docker-compose.yml` | ✅ | ⬜ pending |
| 01-02-2 | 02 | 1 | INFRA-04 | integration | `test -f .env.example && grep -q "DATABASE_URL" .env.example && test -f backend/Dockerfile && grep -q "curl" backend/Dockerfile` | ✅ | ⬜ pending |
| 01-02-3 | 02 | 1 | INFRA-03 | integration | `test -f Makefile && grep -q "^start:" Makefile && grep -q "^test:" Makefile && grep -q "^seed:" Makefile` | ✅ | ⬜ pending |
| 01-03-1 | 03 | 2 | API-09 | integration | `test -f backend/app/config.py && grep -q "class Settings(BaseSettings):" backend/app/config.py && grep -q "cors_origins_list" backend/app/config.py` | ✅ | ⬜ pending |
| 01-03-2 | 03 | 2 | API-07, API-08, API-09 | integration | `test -f backend/app/main.py && grep -q "CORSMiddleware" backend/app/main.py && grep -q "RequestValidationError" backend/app/main.py && grep -q "request_id" backend/app/main.py` | ✅ | ⬜ pending |
| 01-03-3 | 03 | 2 | API-07, API-08 | integration | `test -f backend/app/routers/health.py && grep -q "@router.get(\"/health\"" backend/app/routers/health.py && grep -q "SELECT 1" backend/app/routers/health.py` | ✅ | ⬜ pending |
| 01-04-1 | 04 | 3 | DB-06 | performance | `test -f backend/scripts/seed.py && grep -q "bulk_insert_mappings" backend/scripts/seed.py && grep -q "async def seed_database" backend/scripts/seed.py` | ✅ | ⬜ pending |
| 01-05-1 | 05 | 3 | N/A | unit | `test -f backend/pyproject.toml && grep -q "asyncio_mode = \"auto\"" backend/pyproject.toml` | ✅ | ⬜ pending |
| 01-05-2 | 05 | 3 | N/A | integration | `test -f backend/tests/conftest.py && grep -q "async def test_engine" backend/tests/conftest.py && grep -q "async def test_db" backend/tests/conftest.py && grep -q "async def client" backend/tests/conftest.py` | ✅ | ⬜ pending |
| 01-05-3 | 05 | 3 | API-07, API-08 | integration | `test -f backend/tests/test_health.py && grep -q "async def test_health_endpoint_success" backend/tests/test_health.py && test -f backend/tests/test_config.py && grep -q "def test_cors_origins_parsing" backend/tests/test_config.py` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_schema.py` — Integration tests for DB-01 through DB-05 (database schema and indexes verification)
  - `test_logs_table_structure()` — Verifies logs table exists with id, timestamp, message, severity, source columns
  - `test_timestamp_timezone_aware()` — Confirms timestamp column uses timestamptz data type
  - `test_brin_index_exists()` — Checks idx_logs_timestamp_brin exists using BRIN index type
  - `test_btree_indexes_exist()` — Validates idx_logs_severity and idx_logs_source B-tree indexes
  - `test_composite_index_exists()` — Confirms idx_logs_composite on (timestamp DESC, severity, source)

- [ ] `backend/tests/test_seed.py` — Performance test for DB-06 (seed script execution time)
  - `test_seed_performance()` — Executes seed script with 100k logs, asserts completion < 60 seconds

- [ ] `backend/tests/test_cors.py` — Integration test for API-09 (CORS configuration)
  - `test_cors_configuration()` — Validates CORS middleware uses explicit origins from environment, not wildcard

- [ ] `backend/tests/conftest.py` — Already exists from Plan 05, provides shared fixtures
  - `test_engine` fixture — Creates test database engine with table setup/teardown
  - `test_db` fixture — Provides async session for tests
  - `client` fixture — Provides httpx AsyncClient with dependency overrides

- [ ] `backend/pyproject.toml` — Already exists from Plan 05, configures pytest with asyncio_mode=auto

*Note: Plans 01-05 include inline verification commands (bash file checks). Wave 0 test files provide deeper behavior validation beyond file existence.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Services start with single command | INFRA-03 | Requires Docker daemon interaction and user observation of startup logs | 1. Run `make start`<br>2. Verify all 3 services (postgres, backend, frontend) start without errors<br>3. Check `docker-compose ps` shows all services as "Up"<br>4. Visit http://localhost:8000/api/health (should return 200) |
| Frontend hot-reload works | INFRA-02 | Requires editing frontend code and observing browser refresh | 1. Start services with `make start`<br>2. Edit frontend/pages/index.tsx<br>3. Save file<br>4. Verify browser auto-refreshes within 2 seconds |
| Backend hot-reload works | INFRA-02 | Requires editing backend code and observing API restart | 1. Start services with `make start`<br>2. Edit backend/app/main.py (add comment)<br>3. Save file<br>4. Verify uvicorn logs show "Reloading..." message |
| Docker health checks prevent race conditions | INFRA-01 | Requires stopping/starting services and observing startup sequence | 1. Run `docker-compose down`<br>2. Run `docker-compose up -d`<br>3. Watch logs with `docker-compose logs -f backend`<br>4. Verify backend doesn't show "connection refused" errors (waits for postgres health check) |

*Manual verifications should be performed once at end of wave 3 before `/gsd:verify-work`.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (test_schema.py, test_seed.py, test_cors.py)
- [x] No watch-mode flags (all commands use -x or -v for quick exit)
- [x] Feedback latency < 5s (quick command targets < 5s)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-20
