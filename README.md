# Logs Dashboard

A production-ready log management system demonstrating technical excellence across clean architecture, performant database queries, accurate analytics, comprehensive error handling, thorough testing, and clear documentation.

## Documentation

**For understanding the system:**
- [Technical Specification](./docs/technical_spec.md) - Engineering methodology and constraint-driven decision-making
- [Architecture](./docs/ARCHITECTURE.md) - System design, component interactions, and data flow

**For API and database reference:**
- [API Contract](./docs/api/contract.md) - REST endpoints and schemas
- [Database Schema](./docs/sql/schema.md) - PostgreSQL table and index definitions

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

For detailed technology rationale, see [docs/TECHNOLOGY.md](./docs/TECHNOLOGY.md).

## Getting Started

**Prerequisites:** Docker Desktop, Make

### First Time Setup

**1. Clone and configure:**
```bash
git clone <repository-url>
cd logs-dashboard
cp .env.example .env    # Copy environment configuration
```

**2. Start services:**
```bash
make start              # Start all Docker containers
```

**3. Initialize database:**
```bash
make migrate            # Create database schema and indexes
make seed               # Populate with 100k sample logs
```

**4. Access the application:**
- Frontend: http://localhost:3000 (redirects to http://localhost:3000/logs)
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

The application should now be running with 100,000 sample log entries!

## Testing

**Quick commands:**
```bash
make test         # Run all tests
make test-quick   # Skip slow performance tests
make coverage     # Generate coverage reports
```

**Coverage targets:** 80%+ line coverage for backend (pytest-cov) and frontend (Jest).

For detailed testing documentation, see [docs/TESTING.md](./docs/TESTING.md).

## Development

**Common commands:**
```bash
make start     # Start all services
make stop      # Stop all services
make restart   # Restart all services
make logs      # View logs from all services
make test      # Run all tests
make seed      # Populate database with sample data
make migrate   # Run database migrations
make clean     # Remove all containers and volumes (fresh start)
make help      # See all available commands
```

### Project Structure

```
logs-dashboard/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── models/       # Database models
│   │   ├── routers/      # API endpoints
│   │   └── schemas/      # Pydantic schemas
│   └── tests/            # Backend tests
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities and API client
│   └── __tests__/        # Frontend tests
├── docs/                 # Documentation
│   ├── TESTING.md        # Testing guide
│   ├── ARCHITECTURE.md   # System design
│   ├── TECHNOLOGY.md     # Technology choices
│   └── decisions/        # Architecture Decision Records (ADRs)
├── docker-compose.yml    # Container orchestration
├── Makefile              # Command shortcuts
└── .env                  # Environment configuration
```

## Architecture

The system uses a three-tier architecture with cursor-based pagination, streaming CSV export, and timezone-aware aggregations.

**Key patterns:**
- Cursor-based pagination for constant-time queries
- BRIN + composite B-tree indexes for time-series optimization
- Server Components for SSR performance
- URL state management for shareable links

For detailed architecture documentation, see [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md).

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

## Troubleshooting

### "ECONNREFUSED" error when accessing frontend

**Symptom:** Frontend shows "fetch failed" with ECONNREFUSED error

**Cause:** Missing `API_URL` environment variable for Docker networking

**Solution:** Ensure your `.env` file contains `API_URL=http://backend:8000` (should be present if copied from `.env.example`), then restart:
```bash
docker-compose restart frontend
```

### "relation 'logs' does not exist" error

**Symptom:** Backend shows `sqlalchemy.exc.ProgrammingError: relation "logs" does not exist`

**Cause:** Database migrations haven't been run

**Solution:**
```bash
make migrate     # Create database schema
make seed        # Populate with sample data
```

### Port already in use

**Symptom:** Error starting services because port 3000, 8000, or 5432 is already in use

**Solution:** Stop other services using those ports, or modify port mappings in `docker-compose.yml`

## Related Documentation

- [docs/TESTING.md](./docs/TESTING.md) - Comprehensive testing guide
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) - System design and component interactions
- [docs/TECHNOLOGY.md](./docs/TECHNOLOGY.md) - Technology choices and rationale
- [docs/decisions/](./docs/decisions/) - Architecture Decision Records (ADRs)
- [docs/README.md](./docs/README.md) - Documentation index

## License

MIT
