---
phase: 01-foundation-database
plan: 01
subsystem: database-schema
tags: [database, sqlalchemy, alembic, postgresql, indexes]
completed: 2026-03-20

# Dependency Graph
requires: []
provides:
  - database-models
  - async-session-factory
  - alembic-migrations
  - optimized-indexes
affects:
  - backend/app/models.py
  - backend/app/database.py
  - backend/alembic/*

# Tech Stack
added:
  - SQLAlchemy 2.0.48 (async ORM)
  - psycopg 3.3.3 (async PostgreSQL driver)
  - Alembic 1.18.4 (migrations)
  - Pydantic 2.12.5 (validation)
  - FastAPI 0.135.1
  - Uvicorn 0.42.0

patterns:
  - AsyncEngine with connection pooling
  - AsyncSession with expire_on_commit=False
  - BRIN index for time-series queries
  - B-tree composite index for multi-column filtering
  - Alembic async migration configuration

# Key Files
created:
  - backend/requirements.txt
  - backend/app/__init__.py
  - backend/app/models.py
  - backend/app/database.py
  - backend/alembic.ini
  - backend/alembic/env.py
  - backend/alembic/versions/001_create_logs_table.py

modified: []

# Key Decisions
decisions:
  - Used TIMESTAMP(timezone=True) for timestamptz column type to prevent timezone bugs
  - Configured expire_on_commit=False to prevent greenlet_spawn errors in async contexts
  - Set pool_pre_ping=True to validate connections and handle database restarts gracefully
  - Created BRIN index with pages_per_range=128 and autosummarize=on for time-series optimization
  - Used composite B-tree index (timestamp DESC, severity, source) instead of BRIN for multi-column filtering
  - Manually created migration instead of autogenerate to ensure exact index configuration

# Metrics
duration_seconds: 239
tasks_completed: 3
files_created: 7
commits: 3
---

# Phase 01 Plan 01: Database Schema with Optimized Indexes Summary

Production-ready PostgreSQL schema with SQLAlchemy async models, Alembic migrations, and optimized indexes (BRIN for time-series, B-tree composite for multi-column filtering).

## What Was Built

Created the foundational database layer with:
- SQLAlchemy Log model using timestamptz column type (stores UTC, prevents timezone bugs)
- Async database engine with connection pooling (pool_size=20, max_overflow=10)
- Alembic configured for async migrations with Base.metadata import
- Initial migration with optimized indexes:
  - BRIN index on timestamp (small footprint, fast for sequential time-series data)
  - B-tree indexes on severity and source (efficient equality filtering)
  - Composite B-tree index on (timestamp DESC, severity, source) for multi-column queries

## Implementation Details

### SQLAlchemy Models (backend/app/models.py)
- Log model with 5 columns: id, timestamp, message, severity, source
- Uses `TIMESTAMP(timezone=True)` to generate PostgreSQL timestamptz column
- Follows SQLAlchemy 2.0 declarative style with DeclarativeBase

### Async Database Configuration (backend/app/database.py)
- AsyncEngine with pool_pre_ping=True (validates connections before use)
- AsyncSession with expire_on_commit=False (prevents attribute expiration in async contexts)
- Connection pooling configured for FastAPI concurrency (20 persistent + 10 overflow connections)
- get_db() async generator for FastAPI dependency injection

### Alembic Setup
- Configured env.py for async operation with asyncio.run()
- Imports Base.metadata from app.models for autogenerate support
- Set compare_type=True to detect column type changes (e.g., timestamp vs timestamptz)
- Database URL configured in alembic.ini

### Initial Migration (001_create_logs_table.py)
- Manual migration (not autogenerate) to ensure exact index configuration
- BRIN index with pages_per_range=128 (default, optimal for sequential data) and autosummarize=on (automatic maintenance)
- Composite B-tree index with column order: timestamp (highest cardinality), severity, source
- DESC clause on timestamp for "recent logs first" query pattern
- Complete downgrade() function for rollback support

## Deviations from Plan

None - plan executed exactly as written.

## Performance Considerations

### Index Strategy
- **BRIN on timestamp**: 10-100x smaller than B-tree, optimal for sequential time-series insertions
- **B-tree composite**: PostgreSQL uses left-to-right matching, timestamp first enables range queries + filtering
- **DESC on timestamp**: Optimizes common "recent logs first" query pattern without reverse scan

### Connection Pooling
- pool_size=20: Handles concurrent FastAPI requests without connection overhead
- max_overflow=10: Provides headroom during traffic spikes
- pool_pre_ping=True: Prevents "connection closed" errors after database restarts
- pool_recycle=3600: Recycles connections every hour to prevent stale connections

## Testing Notes

All verification commands passed:
- models.py contains TIMESTAMP(timezone=True)
- database.py contains expire_on_commit=False and pool_pre_ping=True
- alembic/env.py imports Base and uses asyncio.run()
- migration contains all 4 required indexes with correct configuration

## Next Steps

Plan 01-02 will:
- Create Docker Compose configuration for postgres, backend, frontend services
- Configure environment variables and bind mounts for hot-reload
- Add health checks for service orchestration

## Commits

- 6147240: feat(01-01): create SQLAlchemy models and async database configuration
- df7740b: feat(01-01): configure Alembic for async migrations
- ee9463f: feat(01-01): create initial migration with optimized indexes

## Self-Check: PASSED

All files and commits verified:
- backend/requirements.txt: FOUND
- backend/app/__init__.py: FOUND
- backend/app/models.py: FOUND
- backend/app/database.py: FOUND
- backend/alembic.ini: FOUND
- backend/alembic/env.py: FOUND
- backend/alembic/versions/001_create_logs_table.py: FOUND

Commits:
- 6147240: FOUND
- df7740b: FOUND
- ee9463f: FOUND

