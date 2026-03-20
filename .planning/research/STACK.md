# Stack Research

**Domain:** Log Management & Analytics Dashboard
**Researched:** 2026-03-20
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **FastAPI** | 0.135.1 | Python backend API framework | Modern, fast ASGI framework with automatic OpenAPI docs, native async support, and excellent type hint integration. Industry standard for Python APIs in 2025. |
| **PostgreSQL** | 18.x | Relational database | Most advanced open-source RDBMS. Excellent support for indexing time-series data, JSONB for structured logs, and proven scalability to millions of rows. |
| **Next.js** | 15+ | React framework for frontend | Production-grade React framework with App Router, Server Components, and built-in optimizations. Standard choice for modern React dashboards. |
| **Python** | 3.10+ | Backend runtime | Required for FastAPI, SQLAlchemy 2.0, and modern type hints. Python 3.10+ enables structural pattern matching and improved type annotations. |
| **Node.js** | 18+ LTS | Frontend runtime | Required for Next.js. Version 18+ is LTS with stable features for production deployment. |
| **Docker Compose** | 2.x | Local development orchestration | Standard tool for multi-container development environments. Simplifies database + backend + frontend coordination. |

### Backend Stack

#### Database & ORM

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| **SQLAlchemy** | 2.0.48 | Async ORM | Industry-standard Python ORM. Version 2.0 brings mature async support with AsyncSession and AsyncEngine, essential for FastAPI performance. |
| **psycopg** | 3.3.3 | PostgreSQL adapter | Modern PostgreSQL driver (successor to psycopg2) with native async support. Required for SQLAlchemy async with PostgreSQL. |
| **Alembic** | 1.18.4 | Database migrations | Official migration tool for SQLAlchemy. Handles schema versioning and evolution with confidence. |

#### API Layer

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **Pydantic** | 2.12.5 | Data validation & serialization | Always. Integrated with FastAPI for request/response validation. Version 2.x brings 5-50x performance improvements. |
| **pydantic-settings** | 2.13.1 | Configuration management | Always. Type-safe environment variable loading with validation. Replaces manual dotenv parsing. |
| **Uvicorn** | 0.42.0 | ASGI server | Always. Lightning-fast ASGI server for running FastAPI. Use with `--workers` for production. |
| **fastapi-pagination** | 0.15.11 | Pagination utilities | For log list endpoints. Provides cursor and page-based pagination with SQLAlchemy integration. |
| **python-jose[cryptography]** | 3.5.0 | JWT handling | If authentication added later. Not needed for MVP (no auth requirement), but industry standard for JWT. |

#### Development Tools

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| **Ruff** | 0.15.7 | Linting & formatting | **Use instead of Black + Flake8 + isort.** 10-100x faster, combines all three tools. Used by FastAPI itself. |
| **mypy** | 1.19.1 | Static type checking | Catch type errors before runtime. Essential for maintaining type safety in FastAPI endpoints. |
| **pytest** | 9.0.2 | Testing framework | Industry standard for Python testing. Simple, powerful, extensive plugin ecosystem. |
| **pytest-asyncio** | 1.3.0 | Async test support | Test async FastAPI endpoints. Allows `await` in test functions with `@pytest.mark.asyncio`. |
| **httpx** | 0.28.1 | HTTP client for testing | Powers FastAPI's TestClient. Also useful for testing external API calls with async support. |

### Frontend Stack

#### Core Framework

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| **React** | 19.2.x | UI library | Latest stable React with concurrent features and improved performance. Industry standard for dashboards. |
| **Next.js** | 15+ | React framework | App Router (stable), Server Components, built-in optimization. Best-in-class DX for React apps. |
| **TypeScript** | 5.5+ | Type safety | Required by Zod 4. Catches errors at compile time, improves IDE experience, mandatory for production React. |

#### UI & Styling

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **Tailwind CSS** | 4.2+ | Utility-first CSS framework | Always. Rapid UI development with consistent design system. Ships <10kB to production. |
| **shadcn/ui** | Latest | Component library | For dashboard UI (tables, cards, forms). Copy-paste components built on Radix UI. Customizable, accessible. |
| **Recharts** | 2.x | Chart library | For analytics dashboard. React-friendly, declarative API, works seamlessly with Next.js Server Components. |

#### Data Management

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **TanStack Query v5** | 5.x | Server state management | For API data fetching, caching, and synchronization. Eliminates manual loading states and cache management. |
| **Zod** | 4.x | Schema validation | For form validation and API response parsing. TypeScript-first with zero dependencies. Works with React Hook Form. |
| **React Hook Form** | 7.x | Form handling | For log creation form. Minimal re-renders, built-in validation, integrates with Zod for schema validation. |
| **Axios** | 1.x | HTTP client | Alternative to fetch. Better error handling, request/response interceptors, TypeScript support. Use with TanStack Query. |

#### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **ESLint** | 10.0.3+ | JavaScript/TypeScript linting | Catch errors and enforce code style. Use with Next.js config: `eslint-config-next`. |
| **Prettier** | Latest stable | Code formatting | Consistent formatting across team. Configure to work with Tailwind (prettier-plugin-tailwindcss). |
| **date-fns** | 2.29.3+ | Date/time utilities | For timestamp formatting in log list. Lightweight, tree-shakeable, modern alternative to moment.js. |

### Development Environment

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| **Docker** | 24+ | Containerization | For PostgreSQL service and production builds. |
| **Docker Compose** | 2.x | Multi-container orchestration | Define all services (db, backend, frontend) in one file. |
| **Git** | 2.x | Version control | Standard version control. |

## Installation

### Backend (Python)

```bash
# Core dependencies
pip install fastapi==0.135.1 uvicorn[standard]==0.42.0
pip install sqlalchemy==2.0.48 psycopg==3.3.3 alembic==1.18.4
pip install pydantic==2.12.5 pydantic-settings==2.13.1
pip install fastapi-pagination==0.15.11

# Development dependencies
pip install ruff==0.15.7 mypy==1.19.1
pip install pytest==9.0.2 pytest-asyncio==1.3.0 httpx==0.28.1
```

**requirements.txt:**
```
fastapi==0.135.1
uvicorn[standard]==0.42.0
sqlalchemy==2.0.48
psycopg==3.3.3
alembic==1.18.4
pydantic==2.12.5
pydantic-settings==2.13.1
fastapi-pagination==0.15.11
```

**requirements-dev.txt:**
```
ruff==0.15.7
mypy==1.19.1
pytest==9.0.2
pytest-asyncio==1.3.0
httpx==0.28.1
```

### Frontend (Node.js)

```bash
# Create Next.js app with TypeScript
npx create-next-app@latest logs-dashboard --typescript --tailwind --app

# Core dependencies
npm install @tanstack/react-query axios zod react-hook-form @hookform/resolvers
npm install recharts date-fns

# UI components (shadcn/ui - use CLI)
npx shadcn-ui@latest init
npx shadcn-ui@latest add table card button form select

# Dev dependencies
npm install -D eslint prettier prettier-plugin-tailwindcss
```

**package.json key dependencies:**
```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.0.0",
    "zod": "^4.0.0",
    "react-hook-form": "^7.0.0",
    "@hookform/resolvers": "^3.0.0",
    "recharts": "^2.0.0",
    "date-fns": "^2.29.3"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "eslint": "^10.0.3",
    "prettier": "^3.0.0",
    "prettier-plugin-tailwindcss": "^0.5.0"
  }
}
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| **FastAPI** | Django REST Framework | If team strongly prefers Django ecosystem or needs Django admin interface. |
| **FastAPI** | Flask + extensions | If team prefers more control over components. Flask requires manual async setup and validation. |
| **SQLAlchemy 2.0** | Tortoise ORM | If team wants Django-like ORM syntax. Less mature, smaller community. |
| **PostgreSQL** | TimescaleDB | If log volume exceeds 10M+ rows and time-series queries are primary bottleneck. Adds operational complexity. |
| **Ruff** | Black + Flake8 + isort | If team already has mature tooling config. Ruff is strictly faster and consolidates tools. |
| **TanStack Query** | SWR | If team prefers simpler API. SWR has fewer features (no mutations, less cache control). |
| **Recharts** | Chart.js or D3.js | Chart.js for simpler charts, D3 for complex custom visualizations. Recharts balances ease-of-use with flexibility. |
| **Axios** | Native fetch | If minimizing dependencies. Fetch is built-in but lacks interceptors and better error handling. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **psycopg2** | Legacy driver. No native async support, requires gevent/threading hacks with FastAPI. | **psycopg3** (native async) |
| **Flask without async** | Synchronous WSGI blocks entire worker during DB queries. Poor performance with database-heavy workloads. | **FastAPI** (async ASGI) |
| **Black + Flake8 + isort separately** | Slower, requires configuring 3 tools, compatibility issues. | **Ruff** (combines all 3, 10-100x faster) |
| **Moment.js** | Deprecated, large bundle size (67kB), mutable API causes bugs. | **date-fns** (tree-shakeable, immutable) |
| **create-react-app** | Unmaintained since 2022. Poor performance, outdated build tooling. | **Next.js** or **Vite** |
| **Python < 3.10** | Missing modern type hints (union `|` syntax, structural pattern matching). SQLAlchemy 2.0 and Pydantic 2 optimized for 3.10+. | **Python 3.10+** |
| **SQLAlchemy 1.x** | Legacy ORM. Async support bolted on, not native. Version 2.0 is mature and production-ready. | **SQLAlchemy 2.0** |
| **Mongoose (MongoDB)** | Wrong tool for structured time-series data. Logs need relational queries, JOINs, efficient time-range indexing. | **PostgreSQL + SQLAlchemy** |

## Stack Patterns by Use Case

### For This Project (Log Management Dashboard)

**Backend:**
- FastAPI + SQLAlchemy async + PostgreSQL
- Ruff for linting/formatting (replaces Black + Flake8 + isort)
- pytest + pytest-asyncio + httpx for testing
- Alembic for schema migrations
- Uvicorn with `--workers` for production

**Frontend:**
- Next.js 15 (App Router) + React 19 + TypeScript
- Tailwind CSS + shadcn/ui for UI
- TanStack Query for data fetching
- Recharts for analytics charts
- React Hook Form + Zod for forms

**Reasoning:**
- Async-first stack handles 100k+ logs efficiently
- Type safety across stack (TypeScript + Python type hints)
- Modern tooling minimizes boilerplate
- Component libraries accelerate development
- Production-proven at scale

### If Scaling Beyond 10M Logs

**Add:**
- **TimescaleDB extension** for PostgreSQL (time-series optimization)
- **Redis** for API response caching
- **Celery** for background aggregation jobs

**Change:**
- Move from Uvicorn to **Gunicorn + Uvicorn workers** with multiple processes
- Add **database read replicas** for analytics queries

### If Real-Time Updates Needed (Out of Scope but Future)

**Add:**
- **WebSockets** (FastAPI has built-in support)
- **Server-Sent Events (SSE)** for simpler one-way updates
- **React Query subscriptions** for real-time UI updates

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| FastAPI 0.135.1 | Pydantic 2.12.5 | FastAPI 0.100+ requires Pydantic v2. Not compatible with Pydantic v1. |
| SQLAlchemy 2.0.48 | psycopg 3.3.3 | Use `psycopg` (v3), not `psycopg2`. Connection string: `postgresql+psycopg://` |
| SQLAlchemy 2.0.48 | Alembic 1.18.4 | Alembic 1.18+ fully supports SQLAlchemy 2.0 async patterns. |
| Next.js 15+ | React 19.2+ | Next.js 15 uses React 19 Canary features. Use React 19 stable. |
| Zod 4.x | TypeScript 5.5+ | Zod 4 requires TypeScript 5.5+ with strict mode enabled. |
| TanStack Query v5 | React 18-19 | Version 5 supports React 18+. Use `@tanstack/react-query` (v5), not `react-query` (v3, deprecated). |
| Python 3.10-3.14 | All backend deps | Tested range. Python 3.13+ recommended for performance improvements. |

## Key Architecture Decisions

### Backend: Async Throughout

**Why:** Log dashboards are I/O-bound (database queries dominate). Async allows handling multiple requests concurrently without blocking threads.

**Pattern:**
```python
# Use AsyncSession, not Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine("postgresql+psycopg://...")
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@app.get("/logs")
async def get_logs():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Log))
        return result.scalars().all()
```

### Frontend: Server Components + Client Components

**Why:** Next.js 15 App Router enables Server Components by default. Reduces JavaScript shipped to client, improves performance.

**Pattern:**
- **Server Components** (default): Static content, initial data fetching, SEO
- **Client Components** (`"use client"`): Interactive UI (forms, charts, filters)

### Database: Index for Query Patterns

**Why:** Log queries filter by timestamp, severity, and source. Without indexes, queries scan entire table (slow at 100k+ rows).

**Required indexes:**
```sql
CREATE INDEX idx_logs_timestamp ON logs(timestamp DESC);
CREATE INDEX idx_logs_severity ON logs(severity);
CREATE INDEX idx_logs_source ON logs(source);
CREATE INDEX idx_logs_composite ON logs(timestamp DESC, severity, source);
```

### Testing: Integration Over Unit

**Why:** FastAPI apps are thin—most logic is in database queries and API contracts. Integration tests provide better coverage.

**Pattern:**
```python
def test_get_logs_with_filter():
    response = client.get("/logs?severity=ERROR")
    assert response.status_code == 200
    assert all(log["severity"] == "ERROR" for log in response.json())
```

## Sources

- **FastAPI 0.135.1** — https://pypi.org/project/fastapi/ (MEDIUM confidence: official PyPI)
- **SQLAlchemy 2.0.48** — https://pypi.org/project/sqlalchemy/, https://docs.sqlalchemy.org/20/ (HIGH confidence: official docs + PyPI)
- **psycopg 3.3.3** — https://pypi.org/project/psycopg/ (MEDIUM confidence: official PyPI)
- **Pydantic 2.12.5** — https://pypi.org/project/pydantic/ (MEDIUM confidence: official PyPI)
- **Next.js 15+** — https://nextjs.org (MEDIUM confidence: official site, exact version not stated)
- **React 19.2** — https://react.dev (MEDIUM confidence: official site)
- **PostgreSQL 18.x** — https://www.postgresql.org (MEDIUM confidence: official site, latest major version)
- **Ruff 0.15.7** — https://pypi.org/project/ruff/ (HIGH confidence: official PyPI, confirmed used by FastAPI)
- **TanStack Query v5** — https://tanstack.com/query/latest (MEDIUM confidence: official docs)
- **Zod 4.x** — https://zod.dev (MEDIUM confidence: official site)
- **shadcn/ui** — https://ui.shadcn.com (MEDIUM confidence: official site)
- **Recharts** — https://ui.shadcn.com (MEDIUM confidence: mentioned in shadcn docs)
- **Python type hints + async patterns** — Training data + FastAPI/SQLAlchemy official docs (HIGH confidence)

---
*Stack research for: Log Management & Analytics Dashboard*
*Researched: 2026-03-20*
*Confidence: HIGH for backend (official sources), MEDIUM for frontend (some version details from official sites but not all explicitly versioned)*
