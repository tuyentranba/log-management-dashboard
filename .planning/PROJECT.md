# Logs Dashboard

## What This Is

A web-based log management and analytics dashboard built as a technical assessment/portfolio piece. Users can create, view, edit, and delete logs through a clean interface, filter and search across thousands of log entries, and view aggregated analytics through charts showing trends over time and severity distributions. The application demonstrates production-ready full-stack development with FastAPI, PostgreSQL, and Next.js.

## Core Value

Demonstrate technical excellence across all dimensions - clean architecture, performant database queries, accurate analytics, comprehensive error handling, thorough testing, and clear documentation. Every component must showcase production-ready development practices.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Users can create new log entries with timestamp, message, severity, and source
- [ ] Users can view a paginated list of all logs
- [ ] Users can search and filter logs by date range, severity, or source
- [ ] Users can sort logs by any column
- [ ] Users can view detailed information for a single log
- [ ] Users can view an analytics dashboard with aggregated log metrics
- [ ] Dashboard displays a chart showing log count trends over time
- [ ] Dashboard displays a histogram of log severity distribution
- [ ] Dashboard filters work for date range, severity, and source
- [ ] Users can export filtered log data as CSV
- [ ] REST API provides create and read endpoints for logs
- [ ] REST API provides query endpoints with filtering by date range, severity, source
- [ ] REST API provides aggregated data endpoints for analytics
- [ ] Database schema includes logs table with timestamp, message, severity, source columns
- [ ] Database queries are optimized with proper indexing for production scale (100k+ logs)
- [ ] Input validation on all API endpoints
- [ ] Comprehensive error handling with meaningful error messages
- [ ] Application runs via docker-compose with all services
- [ ] Seed script populates database with demo data
- [ ] Unit tests cover backend logic
- [ ] Integration tests cover API endpoints
- [ ] README documents setup, running, testing, and design decisions

### Out of Scope

- Edit/delete log entries — Logs are immutable for audit trail integrity
- User authentication/authorization — Single user application, no login required
- Real-time log streaming — Query-based access sufficient for demo
- Multi-tenancy — Focus on single deployment showcase
- Mobile application — Web interface only
- Advanced log parsing — Logs stored as structured data, no parsing needed
- Log retention policies — All logs persisted indefinitely
- Role-based access control — No user system

## Context

**Purpose:** This is a technical assignment to demonstrate full-stack development capabilities. The application should showcase best practices in API design, database optimization, frontend UX, error handling, testing, and deployment.

**Scale considerations:** While this is a demo, it should handle production-scale data (tens to hundreds of thousands of logs) efficiently. Database indexing, query optimization, and pagination strategies should reflect real-world requirements.

**Data model:** Logs have four core attributes:
- `timestamp` - When the log was created
- `message` - The log content/description
- `severity` - Log level (e.g., INFO, WARNING, ERROR, CRITICAL)
- `source` - Where the log originated from (e.g., service name, module)

**User workflow:**
1. View dashboard to understand log trends and severity distribution
2. Filter by date range, severity, or source to investigate specific issues
3. Navigate to log list to see individual entries
4. Search, sort, and paginate through logs
5. Click into log detail to view full information
6. Create new logs manually for testing/demo purposes
7. Export filtered logs as CSV for external analysis

## Constraints

- **Tech stack**: FastAPI (Python backend), PostgreSQL (database), Next.js (React frontend) - prescribed by assignment
- **Deployment**: Must run via docker-compose for easy developer setup
- **Documentation**: README must explain how to run, test, and include design decisions
- **Best practices**: Code must demonstrate input validation, error handling, proper logging
- **Testing**: Must include unit and/or integration tests

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Immutable logs | Logs should not be editable/deletable - preserves audit trail integrity | — Pending |
| No authentication | Assignment focus is on CRUD + analytics, not security | — Pending |
| Seed data script | Need realistic data volume to showcase query performance | — Pending |
| Include all bonus features | Portfolio piece should be comprehensive to stand out | — Pending |
| Production-ready scale | Should handle 100k+ logs to demonstrate proper indexing/optimization | — Pending |

---
*Last updated: 2025-03-15 after initialization*
