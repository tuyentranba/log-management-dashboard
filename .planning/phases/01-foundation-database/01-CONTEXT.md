# Phase 1: Foundation & Database - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Set up foundational infrastructure for the entire application:
- PostgreSQL database with optimized schema (timestamptz, proper indexes)
- Docker containerization for all services (postgres, backend, frontend)
- Seed script to generate 100k realistic test logs
- Minimal FastAPI skeleton with health check, error handling, CORS

This phase delivers the technical foundation. No API endpoints beyond health check, no UI pages - those come in later phases.

</domain>

<decisions>
## Implementation Decisions

### Error Response Format
- Use FastAPI's default format: `{"detail": "message"}` for single errors
- Validation errors: Use FastAPI's default detailed array with `loc`, `msg`, `type` fields
- No stack traces in responses (production-safe, clean responses)
- Include request IDs in error responses for tracing/debugging
- Standard REST HTTP status codes: 400 (validation), 404 (not found), 500 (server error)
- Database connection errors: Return generic 500 "Internal server error" without exposing DB details
- Validation messages: User-friendly tone ("Severity must be INFO, WARNING, ERROR, or CRITICAL")
- Allow duplicate log entries (logs are append-only, no conflict detection)
- Server-side error logging with levels: 400s logged as WARNING, 500s logged as ERROR

### Health Check Endpoint
- Endpoint: `GET /api/health`
- Response format: `{"status": "ok", "database": "connected"}`
- Test database connectivity: Execute `SELECT 1` query to validate DB is reachable
- Public endpoint: No authentication required (standard practice for health checks)
- Unhealthy state: Return HTTP 503 Service Unavailable when DB connection fails

### Docker Configuration
- Services: 3 services (postgres, backend, frontend)
- Volumes: Bind mounts for `./backend` and `./frontend` to enable hot-reload during development
- Database volume: Named volume `postgres_data` for persistence
- Environment variables: Managed via `.env` file (provide `.env.example` in repo)
- Hot-reload: Frontend uses Next.js dev server with fast refresh
- Compose files: Single `docker-compose.yml` (sufficient for demo/portfolio project)
- Health checks: Define healthcheck for postgres and backend services
- Database initialization: Automatic via init script or migrations on container startup
- Developer commands: Provide Makefile with shortcuts (`make start`, `make test`, `make seed`)

### Seed Data Generation
- Message realism: Template-based realistic patterns ("User login failed", "API request timeout", "Database query slow")
- Severity distribution: Realistic production ratio
  - 70% INFO
  - 20% WARNING
  - 8% ERROR
  - 2% CRITICAL
- Sources: 5-10 different sources representing microservices architecture
  - Examples: api-service, auth-service, database, frontend, worker, cache, queue
- Timestamp distribution: Evenly spread across last 30 days with realistic daily patterns
- Target: 100k logs generated in under 60 seconds (bulk insert performance)

### Claude's Discretion
- Exact Docker image versions (use latest stable)
- FastAPI project structure (routers, dependencies, middleware)
- Database migration tool choice (Alembic or raw SQL)
- Seed script implementation details (Python faker library, batch size)
- Logging library configuration (structlog, python-json-logger, or standard logging)

</decisions>

<canonical_refs>
## Canonical References

No external specs - requirements are fully captured in decisions above and in:
- `.planning/PROJECT.md` - Project vision and constraints
- `.planning/REQUIREMENTS.md` - Specific requirements DB-01 through DB-06, INFRA-01 through INFRA-04, API-07 through API-09
- `.planning/research/STACK.md` - Technology stack decisions (FastAPI 0.135.1, SQLAlchemy 2.0.48 async, PostgreSQL 18.x)
- `.planning/research/PITFALLS.md` - Critical pitfalls to avoid (cursor pagination, composite indexes, timestamptz)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
None - this is a greenfield project (first phase)

### Established Patterns
None - patterns will be established during this phase

### Integration Points
This phase creates the foundational integration points:
- Database connection pool (SQLAlchemy async engine)
- FastAPI app instance with CORS, error handlers, logging
- Docker network for service communication
- Environment variable configuration system

</code_context>

<specifics>
## Specific Ideas

- Bind mounts ensure reproducibility: Anyone cloning the repo can run `docker-compose up` and get identical environment with hot-reload
- Health check must test DB connectivity (not just return 200) to catch connection issues early
- Seed data with realistic severity distribution (70/20/8/2) makes dashboard demos more convincing
- Makefile provides consistent command interface regardless of platform

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation-database*
*Context gathered: 2026-03-20*
