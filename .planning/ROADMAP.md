# Roadmap: Logs Dashboard

**Project:** Log Management and Analytics Dashboard
**Created:** 2026-03-20
**Granularity:** Fine
**Total Phases:** 7

## Phases

- [x] **Phase 1: Foundation & Database** - Database schema, indexes, Docker infrastructure, seed data (completed 2026-03-20)
- [x] **Phase 2: Core API Layer** - REST API endpoints with CRUD, pagination, filtering (completed 2026-03-21)
- [ ] **Phase 3: Log Management UI** - Frontend pages for log browsing, search, filter, detail views
- [x] **Phase 03.1: UX Improvements** - Enhanced severity colors, loading states, source column (URGENT) (completed 2026-03-22)
- [x] **Phase 4: Data Export** - CSV streaming export with filtering (completed 2026-03-22)
- [x] **Phase 04.1: Add search logic in backend** - Message search with ILIKE filtering (URGENT) (completed 2026-03-23)
- [x] **Phase 5: Analytics Dashboard** - Aggregated metrics, charts, time-series visualizations (completed 2026-03-25)
- [x] **Phase 05.1: Analytics Dashboard UX Polish** - Spacing/padding refinement and visual time range filtering (URGENT) (completed 2026-03-25)
- [x] **Phase 05.2: Update and Delete CRUD Operations** - PUT/DELETE endpoints with frontend edit/delete UI (URGENT) (completed 2026-03-26)
- [x] **Phase 05.3: Migrate Create to Modal** - Modal-based create form matching edit/delete pattern (URGENT) (completed 2026-03-26)
- [ ] **Phase 6: Testing** - Unit and integration tests with performance validation
- [ ] **Phase 7: Documentation** - README, design decisions, setup instructions

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Database | 5/5 | Complete   | 2026-03-20 |
| 2. Core API Layer | 3/3 | Complete | 2026-03-21 |
| 3. Log Management UI | 4/5 | In Progress|  |
| 03.1 UX Improvements | 1/1 | Complete   | 2026-03-22 |
| 4. Data Export | 2/2 | Complete | 2026-03-22 |
| 04.1 Add search logic | 1/1 | Complete | 2026-03-23 |
| 5. Analytics Dashboard | 2/2 | Complete   | 2026-03-25 |
| 05.1 Analytics UX Polish | 1/1 | Complete   | 2026-03-25 |
| 05.2 Update/Delete CRUD | 2/2 | Complete   | 2026-03-26 |
| 05.3 Migrate Create Modal | 1/1 | Complete   | 2026-03-26 |
| 6. Testing | 0/? | Not started | - |
| 7. Documentation | 0/? | Not started | - |

## Phase Details

### Phase 1: Foundation & Database
**Goal:** Database schema with production-ready indexes and Docker infrastructure exist, enabling all subsequent development

**Depends on:** Nothing (first phase)

**Requirements:** DB-01, DB-02, DB-03, DB-04, DB-05, DB-06, INFRA-01, INFRA-02, INFRA-03, INFRA-04, API-07, API-08, API-09

**Success Criteria** (what must be TRUE):
1. PostgreSQL database runs via docker-compose with logs table containing id, timestamp (timestamptz), message, severity, source columns
2. Database has BRIN index on timestamp, B-tree indexes on severity and source, and composite index on (timestamp, severity, source)
3. Seed script can populate database with 100k logs in under 60 seconds
4. FastAPI application starts via docker-compose and returns health check at /api/health
5. API returns proper HTTP status codes (400 for validation errors, 500 for server errors) with JSON error messages
6. CORS is configured with explicit allowed origins (not wildcard)

**Plans:** 5/5 plans complete

Plans:
- [x] 01-01-PLAN.md — Database schema and migrations (SQLAlchemy models, Alembic, indexes)
- [x] 01-02-PLAN.md — Docker infrastructure (docker-compose, Dockerfiles, Makefile, .env)
- [x] 01-03-PLAN.md — FastAPI foundation (app structure, health endpoint, CORS, error handlers)
- [x] 01-04-PLAN.md — Seed script (100k log generation with realistic data)
- [x] 01-05-PLAN.md — Test infrastructure (pytest setup, fixtures, initial tests)

---

### Phase 2: Core API Layer
**Goal:** Complete REST API for log CRUD operations with cursor pagination, filtering, and sorting is operational

**Depends on:** Phase 1 (requires database schema and API structure)

**Requirements:** API-01, API-02, API-03, API-04, LOG-01, LOG-02, LOG-03, LOG-04, LOG-05

**Success Criteria** (what must be TRUE):
1. User can POST to /api/logs with timestamp, message, severity, source and receive 201 response with created log
2. User can GET /api/logs with cursor pagination and receive consistent page boundaries (no duplicate or missing logs across pages)
3. User can GET /api/logs/{id} and receive full log details or 404 if not found
4. User can filter logs by date range, severity, or source using query parameters and receive only matching results
5. User can apply multiple filters simultaneously (e.g., severity=ERROR + source=api-service) and receive correct intersection
6. User can sort logs by timestamp, severity, or source in ascending or descending order
7. Pagination works correctly with 100k+ logs without performance degradation (page 100+ loads in under 500ms)

**Plans:** 3/3 plans complete

Plans:
- [x] 02-01-PLAN.md — Pydantic schemas and cursor utilities (data contracts, pagination primitives)
- [x] 02-02-PLAN.md — POST and GET-by-ID endpoints (basic CRUD operations)
- [x] 02-03-PLAN.md — List endpoint with pagination, filtering, sorting (complex queries)

---

### Phase 3: Log Management UI
**Goal:** Users can browse, search, filter, sort, and view logs through a responsive web interface

**Depends on:** Phase 2 (requires API endpoints)

**Requirements:** UI-01, UI-02, UI-03, UI-05, UI-06, UI-07, UI-08, UI-09, FILTER-01, FILTER-02, FILTER-03, FILTER-04, FILTER-05, FILTER-06, FILTER-07

**Success Criteria** (what must be TRUE):
1. User can navigate to log list page and see paginated logs with timestamp, message, severity, and source
2. User can search logs by message content using text input and see real-time filtered results
3. User can filter logs by date range (start/end date pickers), severity (dropdown), and source (dropdown)
4. User can apply multiple filters simultaneously and see filter state persist in URL (shareable link)
5. User can click column headers to sort logs by timestamp, severity, or source
6. User can click pagination controls to navigate pages without losing filter/sort state
7. User can click a log row and navigate to detail page showing full log information
8. User can navigate to log creation form, submit new log, and see success confirmation
9. Frontend displays loading spinners during data fetch and error messages for failed requests
10. Interface is responsive and usable on desktop (1920px), laptop (1440px), and tablet (768px) screens

**Plans:** 4/5 plans executed

Plans:
- [ ] 03-01-PLAN.md — Next.js foundation with TypeScript, Tailwind, shadcn/ui setup
- [ ] 03-02-PLAN.md — Log list with infinite scroll and virtual scrolling
- [ ] 03-03-PLAN.md — Filter sidebar with URL state persistence and sorting
- [ ] 03-04-PLAN.md — Log detail modal and create form with validation

---

### Phase 03.1: UX Improvements for Log Filtering

**Goal:** Enhanced visual scanning and user feedback in log table with colored severity tags, loading indicators, and source field display

**Depends on:** Phase 3 (requires log table implementation)

**Requirements:** None (urgent UX improvements - no formal requirement IDs)

**Success Criteria** (what must be TRUE):
1. Severity badges use vibrant, distinct colors (blue for INFO, yellow for WARNING, orange for ERROR, red for CRITICAL) with white text for immediate visual scanning
2. Loading overlay with spinner and message appears over log table when filters update, providing clear feedback without hiding existing data
3. Source column displays between severity and message columns, showing which service generated each log entry
4. All three improvements integrate seamlessly with existing table functionality (sorting, filtering, virtual scrolling, infinite scroll)

**Plans:** 1/1 plans complete

Plans:
- [x] 03.1-01-PLAN.md — Enhance severity colors, add loading overlay, display source column (3 tasks)

---

### Phase 4: Data Export
**Goal:** CSV export of filtered log data from log list page with streaming response handling large datasets

**Depends on:** Phase 2 (requires API filtering), Phase 3 (requires UI for export trigger)

**Requirements:** EXPORT-01, EXPORT-02, EXPORT-03

**Success Criteria** (what must be TRUE):
1. User can click "Export CSV" button from log list page and receive CSV file download
2. CSV export includes all log fields (timestamp, severity, source, message) with proper headers
3. CSV export respects active filters (date range, severity, source, search text)
4. User can export 10k logs without browser memory errors or API timeout (completes in under 30 seconds)
5. Export streams data (FastAPI StreamingResponse) rather than loading full dataset into memory

**Plans:** 2/2 plans complete

Plans:
- [x] 04-01-PLAN.md — Backend streaming CSV export endpoint with filtering/sorting (3 tasks)
- [x] 04-02-PLAN.md — Frontend export button with loading states and download handling (3 tasks)

---

### Phase 04.1: Add search logic in backend

**Goal:** Backend message search functionality using case-insensitive ILIKE filtering on Log.message field, closing gap between frontend SearchInput component and backend implementation

**Depends on:** Phase 4 (requires export endpoint to integrate search)

**Requirements:** FILTER-01

**Success Criteria** (what must be TRUE):
1. User can search logs by message content using search query parameter
2. Search is case-insensitive (searching 'ERROR' matches 'error' in messages)
3. Search performs partial matching (searching 'timeout' matches 'connection timeout occurred')
4. Export respects search filter (WYSIWYG principle)
5. Search works with other filters (severity, source, date range)

**Plans:** 1 plan

Plans:
- [ ] 04.1-01-PLAN.md — Add search parameter to list and export endpoints with ILIKE filtering (3 tasks)

---

### Phase 5: Analytics Dashboard
**Goal:** Users can view aggregated log metrics and visualizations filtered by date range, severity, and source

**Depends on:** Phase 2 (requires API for aggregations), Phase 3 (requires UI foundation)

**Requirements:** ANALYTICS-01, ANALYTICS-02, ANALYTICS-03, ANALYTICS-04, ANALYTICS-05, ANALYTICS-06, ANALYTICS-07, UI-04

**Success Criteria** (what must be TRUE):
1. User can navigate to analytics dashboard and see summary statistics (total log count, counts by severity level)
2. Dashboard displays time-series area chart showing log volume trends over selected time period with auto-adjusted granularity
3. Dashboard displays severity distribution bar chart showing count of logs per severity level
4. User can click severity bar and navigate to /logs with pre-selected severity filter
5. User can select date range presets (Last hour, 6h, 24h, 7d, 30d) and see charts update
6. Analytics queries require date range filter (API returns 400 error if date range missing)
7. Time-series aggregations use UTC-normalized timestamps and display in local timezone
8. Dashboard loads in under 2 seconds with 100k logs and 30-day date range

**Plans:** 2/2 plans complete

Plans:
- [x] 05-01-PLAN.md — Backend analytics endpoint with aggregation queries (3 tasks: schemas, router with date_trunc/GROUP BY, tests)
- [x] 05-02-PLAN.md — Frontend analytics dashboard with Recharts (3 tasks: types/API, page with chart components, navigation)

---

### Phase 05.1: Analytics Dashboard UX Polish (INSERTED)

**Goal:** Polish analytics dashboard with professional spacing/padding and visual time range filtering interface

**Depends on:** Phase 5 (requires functional analytics dashboard)

**Requirements:** None (urgent UX polish - no formal requirement IDs)

**Success Criteria** (what must be TRUE):
1. Dashboard has proper 24px page padding on all sides
2. Major sections (header, filters, stats, charts) have 32px gaps between them
3. Time range filter displays as segmented button group with 6 preset options (1h, 6h, 24h, 7d, 30d, Custom)
4. Custom date range inputs expand inline when Custom button selected
5. All filter changes update URL state and refetch analytics data
6. Stat cards maintain 24px internal padding with proper tinted backgrounds
7. Chart cards maintain 24px internal padding with consistent styling
8. Overall layout feels balanced and professional following Tailwind's 8-point grid system

**Plans:** 1/1 plans complete

Plans:
- [ ] 05.1-01-PLAN.md — Add spacing/padding and create TimeRangeFilter component (3 tasks)

---

### Phase 05.2: Implement Update and Delete CRUD operations - add PUT and DELETE endpoints for logs with frontend edit/delete functionality (INSERTED)

**Goal:** Complete CRUD operations for logs by adding UPDATE (PUT) and DELETE endpoints with frontend modal edit/delete UI

**Depends on:** Phase 5.1 (requires existing modal foundation)

**Requirements:** None (this phase overrides LOG-05 requirement which originally mandated immutability - now supporting full CRUD for demo purposes)

**Success Criteria** (what must be TRUE):
1. API accepts PUT /api/logs/{id} with complete log data and returns 200 with updated log or 404 for non-existent
2. API accepts DELETE /api/logs/{id} and returns 204 No Content on success or 404 for non-existent
3. Updated log persists in database with all new field values
4. Deleted log is permanently removed from database
5. User can click Edit button in LogDetailModal to enter edit mode with pre-filled form
6. User can modify log fields and save changes (modal closes, list refreshes, success toast)
7. User can click Delete button to see confirmation dialog with log details
8. User confirms deletion → log deleted, modal closes, list refreshes, success toast
9. All buttons show loading states during operations and are disabled to prevent double-submit
10. Error handling shows appropriate toast notifications for 404 and validation errors

**Plans:** 2/2 plans complete

Plans:
- [x] 05.2-01-PLAN.md — Backend PUT and DELETE endpoints with integration tests (2 tasks: PUT with 4 tests, DELETE with 3 tests)
- [x] 05.2-02-PLAN.md — Frontend edit/delete modal UI with API integration (3 tasks: API functions, EditForm, modal extension)

---

### Phase 05.3: Migrate create log form to modal design matching edit/delete pattern (INSERTED)

**Goal:** Move create log form from standalone /create page to modal accessible from /logs header, matching edit/delete modal UX pattern

**Depends on:** Phase 05.2 (requires modal pattern established)

**Requirements:** None (urgent UX consolidation - no formal requirement IDs)

**Success Criteria** (what must be TRUE):
1. User can click "+ Create Log" button in logs page header to open create modal
2. Create modal displays CreateForm with all fields (timestamp, message, severity, source)
3. User can close modal via outside click or Escape without warning
4. Successful creation closes modal, shows toast, and refreshes log list
5. /create route returns 404 (completely removed)
6. Sidebar navigation has no Create Log link
7. Create operation preserves log list filter state (no page reload)
8. Modal follows Phase 05.2 pattern (Dialog component, URL state, toast notifications)

**Plans:** 1/1 plans complete

Plans:
- [ ] 05.3-01-PLAN.md — Adapt CreateForm, add modal to logs page, remove /create route (3 tasks)

---

### Phase 6: Testing
**Goal:** Comprehensive test coverage validates correctness and performance of backend logic, API endpoints, and database queries

**Depends on:** Phase 1-5 (tests all implemented functionality)

**Requirements:** TEST-01, TEST-02, TEST-03, TEST-04, TEST-05

**Success Criteria** (what must be TRUE):
1. Backend unit tests cover service layer logic (filtering, sorting, aggregations, CSV generation) with 80%+ code coverage
2. Integration tests cover all API endpoints (/api/logs, /api/logs/{id}, /api/analytics, /api/export) with success and error cases
3. Performance tests verify pagination, filtering, and sorting correctness with 100k+ log dataset
4. Performance tests verify query execution time (list queries under 500ms, analytics under 2s) with 100k+ logs
5. All tests can be run with single command (e.g., `pytest` or `docker-compose run test`) and pass consistently

**Plans:** TBD

---

### Phase 7: Documentation
**Goal:** Complete documentation enables new developers to understand, run, and test the application

**Depends on:** Phase 1-6 (documents all implemented functionality)

**Requirements:** DOC-01, DOC-02, DOC-03, DOC-04, DOC-05

**Success Criteria** (what must be TRUE):
1. README includes step-by-step instructions to start application via docker-compose
2. README includes instructions to run tests with expected output
3. README documents key design decisions (cursor pagination, composite indexes, timezone handling, streaming export)
4. README explains technology choices (FastAPI, PostgreSQL, Next.js) with rationale
5. Code includes inline comments for complex logic (pagination cursor generation, aggregation queries, CSV streaming)

**Plans:** TBD

---

## Coverage Summary

**Total v1 requirements:** 55
**Mapped requirements:** 55
**Unmapped requirements:** 0

All v1 requirements mapped to phases. No orphaned requirements.

---
*Roadmap created: 2026-03-20*
*Last updated: 2026-03-26*
