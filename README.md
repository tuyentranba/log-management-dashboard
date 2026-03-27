# Logs Dashboard

A production-ready log management system demonstrating technical excellence across clean architecture, performant database queries, accurate analytics, comprehensive error handling, thorough testing, and clear documentation.

## Features

- **Log Management**: Create, view, edit, and delete logs with real-time filtering and sorting
- **Advanced Filtering**: Filter by severity, source, date range, and full-text search
- **Analytics Dashboard**: Time-series charts and severity distribution with configurable date ranges
- **CSV Export**: Stream large datasets efficiently with filtered export
- **Performance**: Handles 100k+ logs with sub-500ms query times
- **Comprehensive Testing**: 80%+ test coverage for both backend and frontend

## Technology Stack

**Backend:**
- FastAPI 0.135.1 - Modern, async Python web framework
- SQLAlchemy 2.0.48 - ORM with async support
- PostgreSQL 18 - Time-series optimized with BRIN indexes
- pytest + pytest-cov 6.0.0 - Testing framework with coverage

**Frontend:**
- Next.js 15.5.14 - React framework with Server Components
- React 19.2.4 - Latest React with improved async support
- TypeScript 5.9.3 - Type-safe JavaScript
- Tailwind CSS 3.4.17 - Utility-first CSS framework
- shadcn/ui - Beautiful UI component library
- Jest 29.7.0 + React Testing Library 16.3.2 - Testing framework

**Infrastructure:**
- Docker Compose - Container orchestration
- Alembic - Database migrations

## Getting Started

### Prerequisites

- Docker Desktop installed and running
- Make (included on macOS/Linux, available for Windows)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd logs-dashboard
```

2. Copy the environment configuration:
```bash
cp .env.example .env
```

3. Edit `.env` with your configuration (optional - defaults work out of the box)

4. Start all services:
```bash
make start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### Seeding Data

Populate the database with 100,000 sample logs (completes in <60 seconds):

```bash
make seed
```

## Testing

The project has comprehensive test coverage for both backend and frontend components, demonstrating production-ready quality with automated validation.

### Test Coverage

**Backend:**
- Unit tests for business logic (cursor utilities, schemas, configuration)
- Integration tests for all API endpoints (CRUD, list, analytics, export)
- Performance tests validating query execution times with 100k logs
- Target: 80%+ line coverage (measured by pytest-cov)

**Frontend:**
- Component tests for forms and modals (CreateForm, EditForm, LogDetailModal)
- API integration tests with mocked responses
- Accessibility validation with jest-axe
- Target: 80%+ line coverage (measured by Jest)

### Running Tests

**All tests (backend + frontend):**
```bash
make test
```

**Quick tests (skip slow performance tests):**
```bash
make test-quick
```
Useful for fast feedback during development. Skips tests marked with `@pytest.mark.slow` (~5-10 second run time).

**Tests with coverage reports:**
```bash
make coverage
```

Coverage reports are generated in:
- Backend: `backend/htmlcov/index.html`
- Frontend: `frontend/coverage/lcov-report/index.html`

Open these HTML files in a browser for detailed line-by-line coverage analysis.

### Running Tests Individually

**Backend only:**
```bash
docker-compose exec backend pytest tests/ -v
```

**Frontend only:**
```bash
docker-compose exec frontend npm test -- --passWithNoTests
```

**Specific test file:**
```bash
# Backend
docker-compose exec backend pytest tests/test_logs_crud.py -v

# Frontend
docker-compose exec frontend npm test -- --testPathPattern=create-form.test.tsx
```

### Test Organization

**Backend (`backend/tests/`):**
- `test_config.py` - Configuration loading and validation
- `test_cursor.py` - Cursor pagination utilities
- `test_schemas.py` - Pydantic schema validation
- `test_health.py` - Health endpoint integration tests
- `test_logs_crud.py` - CRUD operations (POST, GET, PUT, DELETE)
- `test_logs_list.py` - List endpoint with filtering and sorting
- `test_export.py` - CSV export streaming
- `test_analytics.py` - Analytics aggregations
- `test_logs_performance.py` - Performance validation with 100k logs (marked `@pytest.mark.slow`)

**Frontend (`frontend/__tests__/`):**
- `components/create-form.test.tsx` - Create log form validation and submission
- `components/edit-form.test.tsx` - Edit log form pre-population and updates
- `components/log-detail-modal.test.tsx` - Modal view/edit mode toggle
- `api/api-integration.test.tsx` - API client functions with mocked fetch

### Test Philosophy

- **Integration over unit:** Tests validate real behavior with real database and API calls (mocking only external dependencies)
- **Minimal mocking:** Backend tests use real PostgreSQL database for accurate validation
- **User-focused frontend tests:** Tests validate user interactions and accessibility (not implementation details)
- **Performance validation:** Hard thresholds ensure queries meet production requirements (<500ms pagination, <2s analytics)
- **Coverage as visibility:** 80% target demonstrates quality without over-testing trivial code

### Performance Test Thresholds

Performance tests (`test_logs_performance.py`) validate query execution times with 100k logs:

| Endpoint | Threshold | Validates |
|----------|-----------|-----------|
| Pagination (page 100+) | <500ms | Cursor pagination efficiency |
| Analytics aggregations | <2000ms | date_trunc and GROUP BY performance |
| CSV export with filters | <3000ms | Streaming response memory efficiency |
| Multi-filter queries | <500ms | Composite index utilization |

Tests fail if thresholds are exceeded, preventing performance regressions.

## Development

### Available Commands

Run `make help` to see all available commands:

```bash
make help
```

Common commands:
- `make start` - Start all services
- `make stop` - Stop all services
- `make restart` - Restart all services
- `make logs` - View logs from all services
- `make test` - Run all tests
- `make seed` - Populate database with sample data
- `make migrate` - Run database migrations
- `make clean` - Remove all containers and volumes (fresh start)

### Project Structure

```
logs-dashboard/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── config.py     # Configuration management
│   │   ├── database.py   # SQLAlchemy setup
│   │   ├── models/       # Database models
│   │   ├── routers/      # API endpoints
│   │   └── schemas/      # Pydantic schemas
│   ├── tests/            # Backend tests
│   └── scripts/          # Utility scripts (seed.py)
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities and API client
│   └── __tests__/        # Frontend tests
├── docker-compose.yml    # Container orchestration
├── Makefile              # Command shortcuts
└── .env                  # Environment configuration
```

## Architecture Highlights

### Backend

- **Cursor-based pagination**: Prevents OFFSET performance degradation with large datasets
- **Composite indexes**: Optimized for multi-column filtering (timestamp, severity, source)
- **Streaming CSV export**: Memory-efficient with FastAPI StreamingResponse
- **Timezone-aware timestamps**: UTC-normalized aggregations with PostgreSQL timestamptz
- **Async SQLAlchemy**: Non-blocking database operations with async/await

### Frontend

- **Server Components**: SSR performance with Next.js 15
- **Client Islands**: Interactive components only where needed
- **Virtual scrolling**: Efficient rendering of large lists with @tanstack/react-virtual
- **URL state management**: Shareable links with nuqs for filters and modals
- **Type safety**: Full TypeScript coverage mirroring backend schemas

## API Documentation

Interactive API documentation is available at http://localhost:8000/docs when the backend is running.

Key endpoints:
- `POST /api/logs` - Create a log entry
- `GET /api/logs` - List logs with filtering, sorting, and pagination
- `GET /api/logs/{id}` - Get a specific log
- `PUT /api/logs/{id}` - Update a log entry
- `DELETE /api/logs/{id}` - Delete a log entry
- `GET /api/analytics` - Get analytics data with time-series and distribution
- `GET /api/export` - Export logs as CSV with streaming

## License

MIT
