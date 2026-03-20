# Architecture Research

**Domain:** Log Management and Analytics Dashboard
**Researched:** 2026-03-20
**Confidence:** MEDIUM-HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                          │
│  Next.js App Router (React Server/Client Components)            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Dashboard   │  │   Log List   │  │  Log Detail  │          │
│  │  (Analytics) │  │  (Search/    │  │    (View)    │          │
│  │              │  │   Filter)    │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┴─────────────────┘                   │
│                            │                                     │
│                      REST API Client                             │
└────────────────────────────┼─────────────────────────────────────┘
                             │ HTTP/JSON
┌────────────────────────────┼─────────────────────────────────────┐
│                      APPLICATION LAYER                           │
│  FastAPI Backend (Python)                                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    Logs      │  │  Analytics   │  │    Export    │          │
│  │   Router     │  │   Router     │  │   Router     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│  ┌──────┴─────────────────┴─────────────────┴───────┐          │
│  │           Dependency Injection Layer              │          │
│  │  (Database Sessions, Shared Services)             │          │
│  └──────┬────────────────────────────────────────────┘          │
│         │                                                        │
│  ┌──────┴─────────────────────────────────────────────┐         │
│  │              Service Layer                          │         │
│  │  (Business Logic, Query Building, Aggregations)    │         │
│  └──────┬──────────────────────────────────────────────┘        │
│         │                                                        │
│  ┌──────┴─────────────────────────────────────────────┐         │
│  │           Data Access Layer (Repository)            │         │
│  │  (SQLModel/SQLAlchemy ORM, Query Execution)        │         │
│  └──────┬──────────────────────────────────────────────┘        │
└─────────┼───────────────────────────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────────────────────────┐
│         │             DATA STORAGE LAYER                         │
│         │                                                        │
│  ┌──────┴─────────────────────────────────────────────┐         │
│  │            PostgreSQL Database                      │         │
│  │                                                     │         │
│  │  ┌──────────────────────────────────────────────┐  │         │
│  │  │  logs table                                  │  │         │
│  │  │  - id (PK, auto-increment)                   │  │         │
│  │  │  - timestamp (indexed with BRIN)             │  │         │
│  │  │  - message (text)                            │  │         │
│  │  │  - severity (varchar, indexed with B-tree)   │  │         │
│  │  │  - source (varchar, indexed with B-tree)     │  │         │
│  │  │  - created_at (timestamp)                    │  │         │
│  │  └──────────────────────────────────────────────┘  │         │
│  │                                                     │         │
│  │  Indexes:                                           │         │
│  │  - BRIN on timestamp (time-series optimization)    │         │
│  │  - B-tree on severity (categorical queries)        │         │
│  │  - B-tree on source (categorical queries)          │         │
│  │  - Composite index on (timestamp, severity)        │         │
│  └─────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **Next.js Frontend** | User interface, client-side state, data presentation | React Server Components for initial load, Client Components for interactivity (filters, sorting) |
| **API Routers** | HTTP endpoint handlers, request validation, response formatting | FastAPI APIRouter classes organized by feature domain |
| **Service Layer** | Business logic, query composition, data aggregation, CSV export generation | Python classes/functions with clear single responsibilities |
| **Repository Layer** | Database queries, ORM operations, transaction management | SQLModel/SQLAlchemy sessions with typed query methods |
| **PostgreSQL Database** | Persistent storage, query execution, indexing, aggregations | Optimized with BRIN indexes for time-series, B-tree for categories |

## Recommended Project Structure

### Backend Structure (FastAPI)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization, router registration
│   ├── config.py                  # Environment variables, settings (Pydantic Settings)
│   ├── database.py                # Database engine, session factory, connection management
│   │
│   ├── models/                    # Database models (SQLModel/SQLAlchemy)
│   │   ├── __init__.py
│   │   └── log.py                 # Log table model
│   │
│   ├── schemas/                   # Request/Response models (Pydantic)
│   │   ├── __init__.py
│   │   ├── log.py                 # LogCreate, LogResponse, LogListResponse
│   │   └── analytics.py           # AnalyticsResponse, TimeSeriesData
│   │
│   ├── routers/                   # API endpoints organized by feature
│   │   ├── __init__.py
│   │   ├── logs.py                # CRUD operations, search, filter, pagination
│   │   ├── analytics.py           # Aggregated queries, trends, distributions
│   │   └── export.py              # CSV export endpoint
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── log_service.py         # Log operations, filtering logic
│   │   ├── analytics_service.py   # Aggregation calculations, time series
│   │   └── export_service.py      # CSV generation logic
│   │
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   └── log_repository.py      # Database queries, ORM operations
│   │
│   └── dependencies.py            # Shared dependencies (DB session, etc.)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures (test database, client)
│   ├── unit/                      # Unit tests for services, utilities
│   │   ├── test_log_service.py
│   │   └── test_analytics_service.py
│   └── integration/               # Integration tests for API endpoints
│       ├── test_logs_api.py
│       └── test_analytics_api.py
│
├── alembic/                       # Database migrations
│   └── versions/
│
├── scripts/
│   └── seed_data.py               # Generate demo log data
│
├── Dockerfile
├── requirements.txt
└── pyproject.toml
```

### Frontend Structure (Next.js)

```
frontend/
├── app/                           # App Router structure
│   ├── layout.tsx                 # Root layout with shared UI
│   ├── page.tsx                   # Home page (redirect to dashboard)
│   │
│   ├── dashboard/                 # Analytics dashboard
│   │   ├── page.tsx               # Dashboard page (Server Component)
│   │   ├── loading.tsx            # Loading skeleton
│   │   └── components/            # Dashboard-specific components
│   │       ├── TimeSeriesChart.tsx
│   │       ├── SeverityHistogram.tsx
│   │       └── DashboardFilters.tsx
│   │
│   ├── logs/                      # Log list and detail
│   │   ├── page.tsx               # Log list page with search/filter
│   │   ├── [id]/
│   │   │   └── page.tsx           # Log detail page
│   │   └── components/
│   │       ├── LogTable.tsx
│   │       ├── LogFilters.tsx
│   │       ├── Pagination.tsx
│   │       └── ExportButton.tsx
│   │
│   └── api/                       # API route handlers (if needed for BFF)
│
├── components/                    # Shared components
│   ├── ui/                        # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   └── Card.tsx
│   └── layout/
│       ├── Header.tsx
│       └── Navigation.tsx
│
├── lib/                           # Utility functions, API client
│   ├── api-client.ts              # Fetch wrapper with error handling
│   ├── types.ts                   # TypeScript types/interfaces
│   └── utils.ts                   # Helper functions
│
├── hooks/                         # Custom React hooks
│   ├── useLogFilters.ts           # Filter state management
│   └── usePagination.ts           # Pagination logic
│
├── public/                        # Static assets
│
├── Dockerfile
├── package.json
└── tsconfig.json
```

### Docker Compose Structure

```
project-root/
├── docker-compose.yml             # Multi-service orchestration
├── .env.example                   # Environment variable template
├── backend/
├── frontend/
└── README.md
```

### Structure Rationale

**Backend Organization:**
- **Layered architecture** separates concerns: routers handle HTTP, services contain business logic, repositories manage data access
- **Feature-based routers** (logs, analytics, export) keep related endpoints together
- **Dependency injection** through FastAPI's `Depends()` enables testability and shared resource management
- **Schemas separate from models** prevents tight coupling between API contracts and database structure

**Frontend Organization:**
- **App Router** leverages Server Components for initial data fetching, reducing client-side JavaScript
- **Feature-based routing** mirrors user workflows (dashboard → logs → detail)
- **Colocation of components** with routes keeps related code together
- **Shared components** in separate directory for reusability across features

**Database Strategy:**
- **BRIN indexes on timestamp** optimize time-series queries for large log volumes (append-only pattern)
- **B-tree indexes on categorical fields** (severity, source) enable fast filtering
- **Composite indexes** optimize common query patterns (e.g., date range + severity filter)

## Architectural Patterns

### Pattern 1: Repository Pattern

**What:** Abstracts database operations behind a clean interface, separating query logic from business logic.

**When to use:** Always for CRUD applications. Enables testing business logic without database, swapping ORMs, and consistent query patterns.

**Trade-offs:**
- **Pros:** Testability, maintainability, clear boundaries
- **Cons:** Additional layer of abstraction, boilerplate for simple queries

**Example:**
```python
# repositories/log_repository.py
from sqlmodel import Session, select
from typing import List, Optional
from models.log import Log
from datetime import datetime

class LogRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, log_id: int) -> Optional[Log]:
        return self.session.get(Log, log_id)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        severity: Optional[str] = None,
        source: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Log]:
        statement = select(Log)

        if severity:
            statement = statement.where(Log.severity == severity)
        if source:
            statement = statement.where(Log.source == source)
        if start_date:
            statement = statement.where(Log.timestamp >= start_date)
        if end_date:
            statement = statement.where(Log.timestamp <= end_date)

        statement = statement.order_by(Log.timestamp.desc())
        statement = statement.offset(skip).limit(limit)

        return self.session.exec(statement).all()

    def create(self, log: Log) -> Log:
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log
```

### Pattern 2: Dependency Injection for Database Sessions

**What:** Use FastAPI's dependency system to provide database sessions to route handlers, ensuring proper lifecycle management.

**When to use:** Always for database operations. Prevents connection leaks, enables transaction management, simplifies testing.

**Trade-offs:**
- **Pros:** Automatic cleanup, testability, consistent pattern
- **Cons:** Requires understanding of FastAPI's DI system

**Example:**
```python
# database.py
from sqlmodel import create_engine, Session

DATABASE_URL = "postgresql://user:password@localhost/logs_db"
engine = create_engine(DATABASE_URL, echo=False)

# dependencies.py
from typing import Generator
from sqlmodel import Session
from database import engine

def get_session() -> Generator[Session, None, None]:
    """Dependency that provides database session."""
    with Session(engine) as session:
        yield session

# routers/logs.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
from dependencies import get_session
from repositories.log_repository import LogRepository
from schemas.log import LogResponse

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/{log_id}", response_model=LogResponse)
def get_log(
    log_id: int,
    session: Session = Depends(get_session)
):
    repo = LogRepository(session)
    log = repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
```

### Pattern 3: Server Components with Client Islands

**What:** Use React Server Components for data fetching and static content, with selective Client Components for interactivity.

**When to use:** Next.js App Router applications. Reduces JavaScript bundle, improves initial load, maintains interactivity where needed.

**Trade-offs:**
- **Pros:** Smaller bundles, better performance, SEO-friendly
- **Cons:** Requires understanding of server/client boundary, some limitations on hooks in Server Components

**Example:**
```typescript
// app/logs/page.tsx (Server Component)
import { LogTable } from './components/LogTable';
import { LogFilters } from './components/LogFilters';

async function getLogs(searchParams: any) {
  const res = await fetch(`${process.env.API_URL}/logs?${new URLSearchParams(searchParams)}`, {
    cache: 'no-store' // Dynamic data
  });
  return res.json();
}

export default async function LogsPage({ searchParams }: { searchParams: any }) {
  const data = await getLogs(searchParams);

  return (
    <div>
      <h1>Logs</h1>
      {/* Client Component for interactive filtering */}
      <LogFilters />
      {/* Server Component for rendering table */}
      <LogTable logs={data.logs} />
    </div>
  );
}

// app/logs/components/LogFilters.tsx (Client Component)
'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useState } from 'react';

export function LogFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [severity, setSeverity] = useState(searchParams.get('severity') || '');

  const handleFilter = () => {
    const params = new URLSearchParams(searchParams);
    if (severity) {
      params.set('severity', severity);
    } else {
      params.delete('severity');
    }
    router.push(`/logs?${params.toString()}`);
  };

  return (
    <div>
      <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
        <option value="">All Severities</option>
        <option value="INFO">INFO</option>
        <option value="WARNING">WARNING</option>
        <option value="ERROR">ERROR</option>
      </select>
      <button onClick={handleFilter}>Apply Filters</button>
    </div>
  );
}
```

### Pattern 4: Service Layer for Business Logic

**What:** Isolate business logic from HTTP and database concerns in dedicated service classes/modules.

**When to use:** When operations involve multiple steps, complex calculations, or orchestration across repositories.

**Trade-offs:**
- **Pros:** Testable without HTTP layer, reusable logic, clear separation of concerns
- **Cons:** Can be overkill for simple CRUD operations

**Example:**
```python
# services/analytics_service.py
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlmodel import Session, select, func
from models.log import Log

class AnalyticsService:
    def __init__(self, session: Session):
        self.session = session

    def get_severity_distribution(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Calculate log count by severity level."""
        statement = select(Log.severity, func.count(Log.id))

        if start_date:
            statement = statement.where(Log.timestamp >= start_date)
        if end_date:
            statement = statement.where(Log.timestamp <= end_date)

        statement = statement.group_by(Log.severity)
        results = self.session.exec(statement).all()

        return {severity: count for severity, count in results}

    def get_time_series(
        self,
        interval: str = "hour",  # hour, day, week
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get log counts over time intervals."""
        # PostgreSQL date_trunc for time bucketing
        if interval == "hour":
            trunc_func = func.date_trunc('hour', Log.timestamp)
        elif interval == "day":
            trunc_func = func.date_trunc('day', Log.timestamp)
        else:
            trunc_func = func.date_trunc('week', Log.timestamp)

        statement = select(
            trunc_func.label('time_bucket'),
            func.count(Log.id).label('count')
        )

        if start_date:
            statement = statement.where(Log.timestamp >= start_date)
        if end_date:
            statement = statement.where(Log.timestamp <= end_date)

        statement = statement.group_by('time_bucket').order_by('time_bucket')
        results = self.session.exec(statement).all()

        return [
            {'timestamp': time_bucket.isoformat(), 'count': count}
            for time_bucket, count in results
        ]
```

### Pattern 5: Response Models Separate from Database Models

**What:** Define Pydantic schemas for API requests/responses separately from SQLModel database models.

**When to use:** Always. Prevents exposing internal database structure, enables API versioning, adds security layer.

**Trade-offs:**
- **Pros:** Security (filter sensitive fields), flexibility (API can differ from DB), validation
- **Cons:** Code duplication between similar models

**Example:**
```python
# models/log.py (Database model)
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Log(SQLModel, table=True):
    """Database table model."""
    __tablename__ = "logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(index=True)
    message: str
    severity: str = Field(index=True)
    source: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Internal fields not exposed to API
    internal_metadata: Optional[str] = None

# schemas/log.py (API schemas)
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class LogCreate(BaseModel):
    """Request schema for creating a log."""
    timestamp: datetime
    message: str = Field(..., min_length=1, max_length=5000)
    severity: str = Field(..., pattern="^(INFO|WARNING|ERROR|CRITICAL)$")
    source: str = Field(..., min_length=1, max_length=255)

class LogResponse(BaseModel):
    """Response schema for a single log."""
    id: int
    timestamp: datetime
    message: str
    severity: str
    source: str
    created_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode

class LogListResponse(BaseModel):
    """Response schema for paginated log list."""
    logs: List[LogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
```

## Data Flow

### Read Request Flow (Log List with Filters)

```
User clicks "Filter by severity: ERROR"
    ↓
Next.js Client Component (LogFilters)
    → Updates URL search params via router.push()
    ↓
Next.js Server Component (LogsPage) re-renders
    → Calls getLogs(searchParams) server-side fetch
    ↓
FastAPI Router (/logs endpoint)
    → Validates query params with Pydantic
    → Injects Session via Depends(get_session)
    ↓
LogRepository.get_all(severity="ERROR")
    → Builds filtered SQLModel query
    → Executes query against PostgreSQL
    ↓
PostgreSQL
    → Uses B-tree index on severity column
    → Returns matching rows
    ↓
LogRepository
    → Returns List[Log] ORM objects
    ↓
FastAPI Router
    → Converts to LogListResponse Pydantic model
    → Serializes to JSON
    ↓
Next.js Server Component
    → Receives JSON response
    → Passes data to LogTable component
    ↓
LogTable renders HTML
    → Sent to browser
    ↓
User sees filtered logs
```

### Write Request Flow (Create Log)

```
User fills create log form and submits
    ↓
Next.js Client Component (LogCreateForm)
    → Calls fetch() to POST /logs
    → Sends LogCreate JSON payload
    ↓
FastAPI Router (/logs POST endpoint)
    → Validates request body against LogCreate schema
    → Injects Session via Depends(get_session)
    ↓
LogRepository.create(log)
    → Creates Log ORM object
    → session.add(log)
    → session.commit() (persists to database)
    ↓
PostgreSQL
    → Inserts row into logs table
    → Auto-generates ID
    → Returns inserted row
    ↓
LogRepository
    → session.refresh(log) to get generated ID
    → Returns Log object
    ↓
FastAPI Router
    → Converts to LogResponse Pydantic model
    → Returns 201 Created with JSON body
    ↓
Next.js Client Component
    → Receives response
    → router.refresh() to revalidate Server Component
    ↓
Server Component refetches data
    → New log appears in list
```

### Analytics Aggregation Flow

```
User navigates to dashboard
    ↓
Next.js Server Component (DashboardPage)
    → Fetches /analytics/severity-distribution
    → Fetches /analytics/time-series
    ↓
FastAPI Analytics Router
    → Injects Session via Depends(get_session)
    → Calls AnalyticsService methods
    ↓
AnalyticsService.get_severity_distribution()
    → Builds aggregation query with GROUP BY
    ↓
PostgreSQL
    → Scans logs table with appropriate indexes
    → Performs aggregation (COUNT, GROUP BY severity)
    → Returns aggregated results
    ↓
AnalyticsService
    → Formats results into dictionary/list
    ↓
FastAPI Router
    → Converts to AnalyticsResponse schema
    → Returns JSON
    ↓
Next.js Server Component
    → Passes data to chart components (TimeSeriesChart, SeverityHistogram)
    ↓
Client Component charts render
    → Interactive visualizations displayed to user
```

### CSV Export Flow

```
User clicks "Export CSV" button
    ↓
Next.js Client Component (ExportButton)
    → Fetches /export/logs.csv with current filters
    → Includes query params (severity, source, date range)
    ↓
FastAPI Export Router
    → Validates query params
    → Injects Session via Depends(get_session)
    → Calls ExportService.generate_csv()
    ↓
ExportService.generate_csv()
    → Uses LogRepository to query filtered logs
    → Iterates results and builds CSV content
    → Uses Python csv module for proper escaping
    ↓
FastAPI Router
    → Returns StreamingResponse with CSV content
    → Sets Content-Disposition header for download
    ↓
Next.js Client Component
    → Triggers browser download
    ↓
User receives logs.csv file
```

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| **0-10K logs/day** | Monolith is ideal. Single FastAPI backend, single PostgreSQL instance, simple indexes. No special optimizations needed. |
| **10K-100K logs/day** | Optimize query performance. Add BRIN indexes for timestamp, composite indexes for common filter combinations, implement database connection pooling (SQLAlchemy pool_size), add Redis caching for analytics aggregations. |
| **100K-1M logs/day** | Consider read replicas. Route analytics queries to read replica. Implement log partitioning in PostgreSQL (partition by date range). Add background job for pre-computing analytics. Consider CDN for frontend assets. |
| **1M+ logs/day** | Specialized log database. Move to dedicated log storage (TimescaleDB extension for PostgreSQL, or Elasticsearch for full-text search). Implement log ingestion queue (e.g., RabbitMQ, Kafka). Separate write and read paths. Microservices for analytics vs. CRUD. |

### Scaling Priorities

1. **First bottleneck: Database query performance on large datasets**
   - **Symptoms:** Slow log list loading, timeouts on filtered queries, analytics dashboard delays
   - **Solutions:**
     - Add BRIN index on timestamp for time-series queries
     - Add composite indexes for common filter patterns (e.g., `(timestamp, severity)`)
     - Implement pagination with cursor-based approach for large result sets
     - Cache analytics results in Redis with time-based invalidation
     - Use `EXPLAIN ANALYZE` to identify slow queries and optimize

2. **Second bottleneck: Concurrent connections to database**
   - **Symptoms:** Connection pool exhausted errors, slow response times under load
   - **Solutions:**
     - Configure SQLAlchemy connection pooling (`pool_size=20, max_overflow=40`)
     - Implement database connection retry logic with exponential backoff
     - Add read replicas and route read-only queries (analytics, list) to replicas
     - Use pgBouncer for connection pooling at database level

3. **Third bottleneck: Analytics computation overhead**
   - **Symptoms:** Dashboard slow to load, aggregation queries timing out
   - **Solutions:**
     - Pre-compute common analytics in background job (hourly/daily)
     - Store aggregated results in separate `analytics_cache` table
     - Use materialized views for complex aggregations
     - Implement Redis caching with 5-15 minute TTL
     - Consider time-series database extension (TimescaleDB)

## Anti-Patterns

### Anti-Pattern 1: Business Logic in Route Handlers

**What people do:** Put complex calculations, data transformations, and business rules directly in FastAPI route handler functions.

**Why it's wrong:**
- Impossible to unit test without mocking HTTP layer
- Code duplication when multiple endpoints need same logic
- Violates Single Responsibility Principle
- Difficult to reuse logic in background jobs or CLI tools

**Do this instead:**
- Extract business logic into service layer classes/functions
- Keep route handlers thin—only handle HTTP concerns (validation, status codes, serialization)
- Inject services via dependency injection
- Unit test services independently, integration test routes

**Example:**
```python
# BAD: Business logic in router
@router.get("/logs")
def get_logs(severity: Optional[str] = None, session: Session = Depends(get_session)):
    # Complex filtering logic in route
    statement = select(Log)
    if severity:
        statement = statement.where(Log.severity == severity)
    # ... more filtering logic
    results = session.exec(statement).all()

    # Calculation in route
    total = len(results)
    return {"logs": results, "total": total}

# GOOD: Business logic in service
@router.get("/logs")
def get_logs(
    severity: Optional[str] = None,
    session: Session = Depends(get_session)
):
    service = LogService(session)
    return service.get_filtered_logs(severity=severity)
```

### Anti-Pattern 2: No Database Indexes for Filter Columns

**What people do:** Create database tables without indexes on columns used in WHERE clauses (severity, source, timestamp).

**Why it's wrong:**
- Forces full table scans on every filtered query
- Performance degrades linearly with data volume
- Kills user experience at production scale (100K+ logs)
- Causes database resource exhaustion under load

**Do this instead:**
- Add B-tree indexes on all columns used in WHERE clauses (severity, source)
- Add BRIN index on timestamp for time-series queries
- Create composite indexes for common filter combinations
- Monitor query plans with `EXPLAIN ANALYZE`
- Consider partial indexes for frequent filter values

**Example:**
```sql
-- BAD: No indexes
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    source VARCHAR(255) NOT NULL
);

-- GOOD: Strategic indexes
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    source VARCHAR(255) NOT NULL
);

-- BRIN for time-series queries (very efficient for append-only data)
CREATE INDEX idx_logs_timestamp_brin ON logs USING BRIN (timestamp);

-- B-tree for categorical filters
CREATE INDEX idx_logs_severity ON logs (severity);
CREATE INDEX idx_logs_source ON logs (source);

-- Composite index for common query pattern
CREATE INDEX idx_logs_timestamp_severity ON logs (timestamp DESC, severity);
```

### Anti-Pattern 3: Fetching All Data in Client Components

**What people do:** Use Client Components with `useEffect` to fetch all data, including initial page load data that doesn't need interactivity.

**Why it's wrong:**
- Delays content display (fetch happens after JavaScript loads)
- Increases JavaScript bundle size unnecessarily
- Poor SEO (content not in initial HTML)
- Waterfall loading (HTML → JS → data)
- Higher server costs (more client requests)

**Do this instead:**
- Use Server Components for initial data fetching
- Only use Client Components for interactive features (filters, sorting)
- Pass data from Server to Client Components via props
- Use server-side fetch with appropriate caching strategies

**Example:**
```typescript
// BAD: Client Component fetching everything
'use client';

export default function LogsPage() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch('/api/logs')
      .then(res => res.json())
      .then(setLogs);
  }, []);

  return <LogTable logs={logs} />; // Client-side rendering
}

// GOOD: Server Component for data, Client Component for interactivity
// app/logs/page.tsx (Server Component)
async function getLogs() {
  const res = await fetch(`${process.env.API_URL}/logs`);
  return res.json();
}

export default async function LogsPage() {
  const data = await getLogs(); // Server-side fetch

  return (
    <>
      <LogFilters /> {/* Client Component for interactivity */}
      <LogTable logs={data.logs} /> {/* Server Component for display */}
    </>
  );
}
```

### Anti-Pattern 4: Not Using Pagination for Large Result Sets

**What people do:** Return all matching logs in a single API response, or implement pagination only in the UI without backend support.

**Why it's wrong:**
- Memory exhaustion on server and client
- Slow response times (serializing thousands of records)
- Poor user experience (loading 100K records into browser)
- Database query performance degradation
- Network bandwidth waste

**Do this instead:**
- Implement offset/limit pagination at database level
- Return paginated responses with metadata (total, page, page_size)
- Set reasonable default page size (e.g., 50-100)
- Consider cursor-based pagination for very large datasets
- Add pagination UI controls in frontend

**Example:**
```python
# BAD: No pagination
@router.get("/logs")
def get_logs(session: Session = Depends(get_session)):
    logs = session.exec(select(Log).order_by(Log.timestamp.desc())).all()
    return {"logs": logs}  # Could be 100K+ logs!

# GOOD: Pagination with metadata
@router.get("/logs", response_model=LogListResponse)
def get_logs(
    page: int = 1,
    page_size: int = 50,
    session: Session = Depends(get_session)
):
    # Validate pagination params
    page = max(1, page)
    page_size = min(100, max(1, page_size))  # Cap at 100

    # Count total
    total = session.exec(select(func.count(Log.id))).one()

    # Fetch page
    offset = (page - 1) * page_size
    logs = session.exec(
        select(Log)
        .order_by(Log.timestamp.desc())
        .offset(offset)
        .limit(page_size)
    ).all()

    return {
        "logs": logs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }
```

### Anti-Pattern 5: Mixing Database Models and API Schemas

**What people do:** Use SQLModel models directly as API response models, exposing internal database structure and fields.

**Why it's wrong:**
- Exposes internal database structure to API consumers
- Cannot version API independently from database schema
- Security risk (accidentally exposing sensitive fields)
- Tight coupling between layers
- Breaks if database schema changes

**Do this instead:**
- Define separate Pydantic schemas for API requests and responses
- Use `response_model` parameter in FastAPI routes
- Convert ORM models to schemas explicitly
- Filter/transform data between layers
- Document API contract separately from database schema

**Example:**
```python
# BAD: Exposing database model directly
from sqlmodel import SQLModel, Field

class Log(SQLModel, table=True):
    id: int
    timestamp: datetime
    message: str
    severity: str
    source: str
    internal_notes: str  # Internal field!
    processing_metadata: str  # Internal field!

@router.get("/logs/{log_id}")
def get_log(log_id: int, session: Session = Depends(get_session)):
    log = session.get(Log, log_id)
    return log  # Exposes internal_notes and processing_metadata!

# GOOD: Separate API schema
# models/log.py
class Log(SQLModel, table=True):
    id: int
    timestamp: datetime
    message: str
    severity: str
    source: str
    internal_notes: str
    processing_metadata: str

# schemas/log.py
class LogResponse(BaseModel):
    """Public API response - only safe fields."""
    id: int
    timestamp: datetime
    message: str
    severity: str
    source: str

    class Config:
        from_attributes = True

# routers/logs.py
@router.get("/logs/{log_id}", response_model=LogResponse)
def get_log(log_id: int, session: Session = Depends(get_session)):
    log = session.get(Log, log_id)
    return log  # FastAPI converts using LogResponse schema
```

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **PostgreSQL Database** | SQLModel/SQLAlchemy ORM with connection pooling | Use SQLALCHEMY_DATABASE_URI from environment variable. Configure pool_size and max_overflow for production. Enable connection retry logic. |
| **Docker Compose** | Multi-service orchestration | Define services: frontend (Next.js on port 3000), backend (FastAPI on port 8000), database (PostgreSQL on port 5432). Use named volumes for database persistence. Environment variables passed via `.env` file. |
| **CSV Export** | FastAPI StreamingResponse | Use Python's `csv` module with `StreamingResponse` for memory-efficient large exports. Set appropriate headers: `Content-Type: text/csv`, `Content-Disposition: attachment; filename="logs.csv"`. |
| **Chart Library** | Recharts or Chart.js in Next.js | Recharts for React-native integration (composable API). Chart.js for broader chart types. Both work in Client Components. Pass aggregated data from Server Components as props. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| **Frontend ↔ Backend** | REST API over HTTP/JSON | Frontend calls backend API at `http://backend:8000` (docker-compose network) or configurable API_URL. CORS configured in FastAPI for development. Use absolute URLs in production. |
| **Router ↔ Service** | Direct function calls with dependency injection | Routers receive services via `Depends()` or instantiate directly with injected dependencies (e.g., `session`). Services return Python objects, routers handle serialization. |
| **Service ↔ Repository** | Direct function calls | Services instantiate repositories with database session. Repositories return ORM objects, services handle transformation to business objects if needed. |
| **Repository ↔ Database** | SQLModel/SQLAlchemy ORM | Repository uses SQLModel `Session` to execute queries. All database operations go through ORM for type safety and query building. Raw SQL only for complex analytics if needed. |

## Build Order Implications

### Recommended Implementation Sequence

**Phase 1: Foundation (Backend Core)**
1. Database schema and migrations (SQLModel models, Alembic setup)
2. Repository layer (basic CRUD operations)
3. FastAPI app structure (main.py, routers, dependencies)
4. Basic logs CRUD endpoints (create, read by ID, list)
5. Request/response schemas (Pydantic models)

**Dependencies:** Database must exist before repositories. Schemas should be defined before routers.

**Phase 2: Frontend Foundation**
1. Next.js app structure (App Router setup)
2. API client utility (fetch wrapper with error handling)
3. Basic log list page (Server Component with table)
4. Navigation and layout components
5. Log detail page

**Dependencies:** Backend logs endpoints must be working for frontend to fetch data.

**Phase 3: Filtering and Search**
1. Backend: Add filtering logic to repository (WHERE clauses)
2. Backend: Update logs list endpoint with query params
3. Frontend: Filter UI components (Client Components)
4. Frontend: URL search params integration
5. Database: Add indexes on filter columns

**Dependencies:** Basic list functionality must work before adding filters.

**Phase 4: Analytics Dashboard**
1. Backend: Service layer for aggregations
2. Backend: Analytics router with endpoints (severity distribution, time series)
3. Backend: Database indexes for aggregation performance
4. Frontend: Dashboard page with charts (Recharts components)
5. Frontend: Dashboard filters (date range picker)

**Dependencies:** Logs data must exist (seed script needed). Chart library must be installed.

**Phase 5: Advanced Features**
1. Backend: CSV export service and endpoint
2. Frontend: Export button with download handling
3. Frontend: Pagination UI components
4. Backend: Sorting support in repository
5. Database: Composite indexes for common query patterns

**Dependencies:** Core functionality must be stable. Performance optimizations come after features work.

**Phase 6: Testing and Deployment**
1. Backend: Unit tests for services and repositories
2. Backend: Integration tests for API endpoints (pytest with TestClient)
3. Frontend: Component tests (if time permits)
4. Docker Compose configuration for all services
5. Seed data script for realistic testing
6. README documentation

**Dependencies:** All features implemented. Docker setup needs all services defined.

### Critical Path

**Must implement in order:**
1. Database schema → Repository → Routers (backend vertical slice)
2. Backend CRUD → Frontend pages (horizontal slice)
3. Basic functionality → Filters → Analytics (feature progression)
4. Features working → Indexes → Caching (performance optimization)

**Can implement in parallel:**
- Backend tests while frontend pages being built
- Dashboard analytics while log filtering being implemented
- Docker configuration while features being developed
- Documentation while testing being written

## Sources

**HIGH Confidence:**
- [FastAPI Documentation - Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) — Official guidance on project structure and APIRouter organization
- [FastAPI Documentation - Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) — Official dependency injection patterns
- [FastAPI Documentation - Response Models](https://fastapi.tiangolo.com/tutorial/response-model/) — Official API schema patterns
- [FastAPI Documentation - Testing](https://fastapi.tiangolo.com/tutorial/testing/) — Official testing patterns with TestClient
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/) — Official ORM and database patterns for FastAPI
- [Next.js Documentation - App Router](https://nextjs.org/docs) — Official architecture for React Server Components
- [Next.js Documentation - Loading UI](https://nextjs.org/docs/app/building-your-application/routing/loading-ui-and-streaming) — Official loading and streaming patterns
- [PostgreSQL Documentation - BRIN Indexes](https://www.postgresql.org/docs/current/brin.html) — Official guidance on time-series indexing
- [React Documentation - Thinking in React](https://react.dev/learn/thinking-in-react) — Official component hierarchy patterns
- [Pydantic Documentation](https://docs.pydantic.dev/latest/) — Official validation and serialization patterns
- [Docker Compose Documentation](https://docs.docker.com/compose/) — Official multi-service orchestration

**MEDIUM Confidence:**
- [Elasticsearch/Kibana Architecture](https://www.elastic.co/guide/en/kibana/current/introduction.html) — Industry-standard log management architecture (used for comparative analysis)

**Notes:**
- BRIN indexes for time-series data verified in official PostgreSQL docs (HIGH confidence)
- FastAPI project structure patterns from official tutorial (HIGH confidence)
- Next.js Server/Client Component split from official docs (HIGH confidence)
- Service/Repository pattern is industry standard (HIGH confidence via training data + official FastAPI structure guidance)
- Recharts information unavailable from direct sources, recommend verification during implementation (LOW confidence)
- Testing structure based on FastAPI official testing docs (HIGH confidence)

---
*Architecture research for: Log Management and Analytics Dashboard*
*Researched: 2026-03-20*
