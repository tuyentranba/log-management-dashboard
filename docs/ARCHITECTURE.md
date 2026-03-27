# System Architecture

Comprehensive architecture overview for the Logs Dashboard project.

## High-Level Overview

The Logs Dashboard is a three-tier web application demonstrating production-ready architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 15)                │
│  ┌──────────────────┐        ┌──────────────────────┐  │
│  │ Server Components│        │  Client Components   │  │
│  │  (SSR, SEO)      │        │  (Interactivity)     │  │
│  └────────┬─────────┘        └──────────┬───────────┘  │
│           │                               │              │
│           └───────────────┬───────────────┘              │
│                           │                              │
└───────────────────────────┼──────────────────────────────┘
                            │ HTTP / REST API
┌───────────────────────────┼──────────────────────────────┐
│                     Backend (FastAPI)                     │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Routers: /api/logs, /api/analytics, /api/export   │ │
│  └────────────────────┬────────────────────────────────┘ │
│                       │                                   │
│  ┌────────────────────┴────────────────────────────────┐ │
│  │  Services: Cursor pagination, CSV streaming,        │ │
│  │            Aggregation logic, Timezone handling     │ │
│  └────────────────────┬────────────────────────────────┘ │
│                       │                                   │
└───────────────────────┼───────────────────────────────────┘
                        │ SQLAlchemy (async ORM)
┌───────────────────────┼───────────────────────────────────┐
│                 Database (PostgreSQL 18)                  │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Table: logs (timestamptz, severity, source, msg)  │ │
│  │  Indexes: BRIN (timestamp), Composite (ts,sev,src) │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

**Architecture Style:** Monorepo with separate frontend/backend services, REST API communication, PostgreSQL persistence.

## Component Interactions

### Data Flow: Log List Page Load

**1. Initial Page Load (Server-Side Rendering):**
```
User requests /logs
  ↓
Next.js Server Component (page.tsx)
  ↓ Fetch initial data
Backend GET /api/logs?limit=50
  ↓ Query with cursor pagination
PostgreSQL (BRIN index + composite index)
  ↓ Return first 50 logs + next_cursor
Server Component renders HTML
  ↓ Ship HTML to browser
User sees logs immediately (SSR performance)
```

**2. Infinite Scroll (Client-Side):**
```
User scrolls to bottom (last 10 items visible)
  ↓
Client Component (useInfiniteScroll hook)
  ↓ Fetch next page
Backend GET /api/logs?cursor={next_cursor}&limit=50
  ↓ Decode cursor, query (timestamp, id) < (cursor_ts, cursor_id)
PostgreSQL (composite index seek)
  ↓ Return next 50 logs + next_cursor
Client Component appends to list
  ↓
Virtual scroll re-renders visible items only
```

**3. Filter Change (Client-Side):**
```
User clicks severity filter checkbox
  ↓
Client Component (LogFilters)
  ↓ Update URL state via nuqs
URL changes: ?severity=ERROR
  ↓ All components using useLogFilters() re-render
useInfiniteScroll detects filter change
  ↓ Reset pagination state, fetch from beginning
Backend GET /api/logs?severity=ERROR&limit=50
  ↓ Apply severity filter in WHERE clause
PostgreSQL (composite index (timestamp, severity))
  ↓ Return filtered logs
Client Component replaces list
```

### Data Flow: Analytics Dashboard

```
User requests /analytics?date_from=...&date_to=...
  ↓
Next.js Server Component (analytics/page.tsx)
  ↓ Fetch analytics data
Backend GET /api/analytics?date_from=...&date_to=...
  ↓ Determine granularity (hour/day/week)
  ↓ Execute 3 queries in parallel:
  │   1. Summary stats (COUNT FILTER for each severity)
  │   2. Time-series (date_trunc + GROUP BY)
  │   3. Severity distribution (GROUP BY severity)
PostgreSQL (BRIN index for date range, aggregations)
  ↓ Return {summary, time_series, severity_distribution}
Server Component renders charts
  ↓ Client Components (Recharts) hydrate for interactivity
User sees analytics instantly (SSR performance)
```

### Data Flow: CSV Export

```
User clicks "Export CSV" button
  ↓
Client Component (ExportButton) shows loading state
  ↓ Fetch with current filters
Backend GET /api/export?severity=ERROR&date_from=...
  ↓ Build query with filters (same as list endpoint)
  ↓ Use StreamingResponse + async generator
PostgreSQL stream() with yield_per(1000)
  ↓ Fetch 1000 rows at a time
  │ Write to CSV (StringIO buffer)
  │ Yield chunk to client
  │ Repeat until query exhausted or 50k row limit
Client receives chunks, builds Blob
  ↓ Create download link (URL.createObjectURL)
Browser downloads CSV file
```

**Key insight:** Streaming prevents memory spike - 50k logs use constant ~10MB memory (not 50k * row_size).

## Backend Architecture

### Layered Structure

```
routers/           # API endpoints (FastAPI routers)
├── logs.py        # CRUD, list, export
├── analytics.py   # Aggregations
└── health.py      # Health check

schemas/           # Pydantic models (validation, serialization)
├── logs.py        # LogCreate, LogResponse, LogListResponse
└── analytics.py   # AnalyticsResponse, TimeSeriesDataPoint

models/            # SQLAlchemy ORM models
└── log.py         # Log model with indexes

utils/             # Pure functions (no dependencies)
└── cursor.py      # encode_cursor, decode_cursor

dependencies.py    # FastAPI dependencies (get_db, etc.)
database.py        # SQLAlchemy engine setup
config.py          # pydantic-settings configuration
main.py            # FastAPI app creation, middleware, exception handlers
```

**Pattern:** Clear separation of concerns - routers handle HTTP, schemas handle validation, models handle persistence, utils handle algorithms.

### Key Design Decisions

See ADRs for detailed rationale:
- [ADR-002: Cursor Pagination](./decisions/002-cursor-pagination.md) - Why cursor over offset
- [ADR-003: Database Indexing](./decisions/003-database-indexing.md) - BRIN + composite B-tree strategy
- [ADR-004: Timezone Handling](./decisions/004-timezone-handling.md) - timestamptz + UTC normalization

**Pagination architecture:**
- Cursor encodes (timestamp, id) as base64 JSON (opaque to clients)
- Query uses composite comparison: `WHERE (timestamp, id) < (cursor_ts, cursor_id) ORDER BY timestamp DESC, id DESC LIMIT N+1`
- Fetch N+1 items to determine has_more (avoids separate COUNT query)
- Composite index (timestamp DESC, id DESC) enables efficient seeks

**CSV streaming architecture:**
- async generator function yields CSV chunks
- SQLAlchemy stream() with yield_per(1000) fetches batches
- StringIO buffer with truncate/seek pattern prevents memory accumulation
- anyio.sleep(0) provides cancellation points for proper cleanup

## Frontend Architecture

### Next.js 15 App Router Structure

```
app/
├── layout.tsx              # Root layout with providers, sidebar
├── page.tsx                # Home (redirects to /logs)
├── logs/
│   ├── page.tsx            # Server Component - fetch initial data
│   └── _components/        # Client Components
│       ├── log-list.tsx    # Infinite scroll, virtual scrolling
│       ├── log-filters.tsx # Filter UI with URL state
│       ├── log-table.tsx   # Table rendering
│       └── log-detail-modal.tsx  # View/edit modal
├── analytics/
│   ├── page.tsx            # Server Component - fetch analytics
│   └── _components/        # Client Components
│       ├── analytics-charts.tsx  # Recharts integration
│       └── time-range-filter.tsx # Date range picker

components/                 # Shared components
├── ui/                     # shadcn/ui primitives (Button, Card, etc.)
└── ...

hooks/                      # Custom hooks
├── use-infinite-scroll.ts  # Pagination state machine
└── use-log-filters.ts      # Shared filter state schema

lib/
├── api.ts                  # API client functions (fetch wrappers)
├── types.ts                # TypeScript types mirroring backend schemas
└── constants.ts            # API_URL, SEVERITY_COLORS
```

**Pattern:** Server Components for initial data fetching (SSR), Client Components for interactivity, custom hooks for reusable logic.

### Key Design Decisions

See ADRs for detailed rationale:
- [ADR-001: Filter Reactivity](./decisions/001-filter-reactivity-refactor.md) - Why URL as single source of truth
- [ADR-005: Frontend Architecture](./decisions/005-frontend-architecture.md) - Server/Client split, hooks, composition

**URL state management:**
- nuqs library provides reactive URL state (useQueryStates hook)
- All components read/write directly to URL (no separate React state)
- Filter changes trigger component re-renders automatically
- Shareable links work by default (all state in URL)

**Virtual scrolling:**
- @tanstack/react-virtual renders only visible rows (~20 items)
- 100k logs render as 100k divs (invisible) but only 20 render DOM
- Infinite scroll loads next page when user scrolls to last 10 items
- Performance: 60fps scrolling even with 10k+ logs in memory

## Database Architecture

### Table Schema

```sql
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,  -- timestamptz
    message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,  -- INFO, WARNING, ERROR, CRITICAL
    source VARCHAR(100) NOT NULL
);
```

**Constraints:**
- `timestamp` is timezone-aware (timestamptz), stored as UTC
- `severity` has enum-like validation at application level (Pydantic schema)
- `id` is auto-incrementing (SERIAL)

### Indexes

**1. BRIN Index on Timestamp (time-series optimization):**
```sql
CREATE INDEX idx_logs_timestamp_brin ON logs USING BRIN (timestamp)
WITH (pages_per_range = 128, autosummarize = on);
```
- Ultra-compact: ~0.1% of table size (100MB table → 100KB index)
- Optimizes time-range queries (date_from/date_to filters)
- pages_per_range=128 means 1 index entry per ~1MB of data
- autosummarize keeps index updated automatically

**2. Composite B-tree Index (multi-column filtering):**
```sql
CREATE INDEX idx_logs_composite ON logs (timestamp DESC, severity, source);
```
- Optimizes multi-column queries (timestamp + severity, timestamp + source, timestamp + severity + source)
- Supports ORDER BY timestamp DESC (default sort)
- Enables efficient cursor pagination with composite key
- ~5% of table size (acceptable trade-off)

**Why this combination:** BRIN handles time-range queries efficiently with minimal storage, composite B-tree handles filtered pagination. Query planner chooses best index per query.

## Performance Characteristics

### Query Performance (100k logs)

| Operation | Time | Index Used |
|-----------|------|------------|
| Pagination page 1 | ~10ms | Composite B-tree |
| Pagination page 100 | ~12ms | Composite B-tree (constant time) |
| Filter by severity | ~50ms | Composite B-tree (prefix scan) |
| Date range query | ~80ms | BRIN index |
| Analytics aggregation | ~1.8s | BRIN + GROUP BY |
| CSV export (50k rows) | ~2.5s | Streaming (constant memory) |

**Testing:** Performance tests in `backend/tests/test_logs_performance.py` validate these thresholds.

### Memory Usage

| Operation | Memory | Pattern |
|-----------|--------|---------|
| Single log query | ~1KB | Row fetching |
| Pagination (50 logs) | ~50KB | Batch fetching |
| Analytics aggregation | ~5MB | Aggregated results only |
| CSV export (50k logs) | ~10MB | Streaming (yield_per=1000) |
| Frontend virtual scroll | ~20MB | Only visible rows rendered |

**Key insight:** Cursor pagination + streaming + virtual scroll enable constant memory usage regardless of dataset size.

## Technology Choices

For detailed rationale, see [TECHNOLOGY.md](./TECHNOLOGY.md).

**Backend:**
- FastAPI - Async Python web framework with auto-generated API docs
- PostgreSQL 18 - BRIN index support, timestamptz, mature time-series optimizations
- SQLAlchemy 2.0 - Async ORM with stream() for batch fetching

**Frontend:**
- Next.js 15 - Server Components for SSR performance, App Router for modern patterns
- React 19 - Latest async features, improved performance
- nuqs - Reactive URL state management (solves filter reactivity problem)

**Infrastructure:**
- Docker Compose - Local development environment, consistent across team
- Alembic - Database migrations with version control

## Related Documentation

- [README.md](../README.md) - Quick start and project overview
- [TESTING.md](./TESTING.md) - Testing guide and coverage reports
- [TECHNOLOGY.md](./TECHNOLOGY.md) - Technology choices and rationale
- [docs/decisions/](./decisions/) - Architecture Decision Records (ADRs)

---

*Last updated: 2026-03-27 (Phase 7 documentation)*
