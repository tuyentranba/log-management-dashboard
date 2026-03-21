# Phase 3: Log Management UI - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Build a Next.js frontend for browsing, searching, filtering, sorting, and viewing logs. Users can navigate between log list, log detail, and log creation pages. The UI consumes the REST API completed in Phase 2.

This phase delivers:
- `/logs` - Main log list page with table, filters, search, sorting, pagination
- Log detail modal - Overlay showing full log information
- `/logs/create` - Form to create new log entries
- Persistent sidebar navigation
- Responsive layout (desktop 1920px, laptop 1440px, tablet 768px)

No analytics dashboard (Phase 5). No CSV export (Phase 4). This phase focuses on core log management UI.

</domain>

<decisions>
## Implementation Decisions

### Page Structure & Navigation
- **Routing**: Separate routes with persistent sidebar navigation
- **Sidebar items**: "Logs" and "Create Log" (Dashboard added in Phase 5)
- **Log detail**: Modal overlay on list page (not separate route) - URL can update via query param
- **Page titles**: Simple H1 only ("Logs", "Create Log") - no breadcrumbs
- **Layout consistency**: Sidebar persists across all pages

### Log List Display
- **Table style**: Borderless table with modern clean aesthetic, subtle row hover
- **Columns**: Severity (as colored badge) + Message (primary content) + Timestamp (right-aligned)
- **Severity badges**: Color-coded backgrounds only (INFO=blue, WARNING=yellow, ERROR=red, CRITICAL=dark red) - no icons
- **Pagination**: Infinite scroll with virtual scrolling (auto-load more on scroll, virtualization for performance)
- **Row interaction**: Hover highlights row background, click anywhere on row opens detail modal
- **Sorting**: Clickable column headers with sort direction icons (▲/▼) - API supports timestamp/severity/source sorting
- **Empty state**: "No logs yet. Create your first log!" with prominent Create Log button

### Filter & Search UI
- **Filter position**: Left sidebar panel next to table (vertical layout)
- **Search input**: Debounced real-time search (300-500ms debounce) - search message content as you type
- **Date range**: Two separate date inputs (Start Date, End Date) - simple HTML date inputs or basic date picker
- **Severity filter**: Multi-select dropdown allowing multiple selections (INFO, WARNING, ERROR, CRITICAL)
- **Source filter**: Dropdown or text input (case-insensitive matching per Phase 2 API)
- **Active filter visibility**: Filter chips above table showing active filters with X to remove ("Severity: ERROR [x]", "Source: api-service [x]")
- **URL state**: Filter state preserved in URL search params (?search=error&severity=ERROR&date_from=2024-01-01) for shareable links
- **Clear filters**: "Reset Filters" button at bottom of filter sidebar panel

### Loading & Error States
- **Loading indicator**: Skeleton rows in table (gray shimmer/pulse animation) - maintains layout, feels fast
- **Error display**: Toast notification (top-right corner) that auto-dismisses - non-blocking for transient errors
- **Optimistic UI**: Form submissions show immediately in list, rollback on API error
- **Retry logic**: Automatic retry (1-2 attempts) for failed requests before showing error to user

### Claude's Discretion
- Exact component library choice (shadcn/ui, Headless UI, or custom)
- Skeleton animation style (pulse, shimmer, wave)
- Toast auto-dismiss timing
- Exact debounce delay (300-500ms range)
- Modal transition animations
- Responsive breakpoint adjustments
- Infinite scroll trigger point (how far from bottom)
- Virtual scroll library (react-window, react-virtual, or custom)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project requirements
- `.planning/PROJECT.md` - Project vision, tech stack (Next.js 15, React 19, TypeScript), constraints
- `.planning/REQUIREMENTS.md` - Requirements UI-01 through UI-09, FILTER-01 through FILTER-07
- `.planning/ROADMAP.md` - Phase 3 success criteria (10 specific truths that must be verified)

### Prior phase context
- `.planning/phases/02-core-api-layer/02-CONTEXT.md` - API response format, pagination strategy, filter parameters, validation rules
- `.planning/phases/01-foundation-database/01-CONTEXT.md` - CORS configuration, error response format

### API contracts
- Backend API base URL: `http://localhost:8000/api` (from docker-compose)
- API endpoints from Phase 2:
  - `GET /api/logs` - List with cursor pagination, filters, sorting
  - `GET /api/logs/{id}` - Single log detail
  - `POST /api/logs` - Create new log
- API response envelope: `{"data": [...], "next_cursor": "...", "has_more": true}`
- Query parameters: `cursor`, `limit`, `date_from`, `date_to`, `severity` (repeated), `source`, `sort`, `order`
- Timestamp format: ISO 8601 with timezone (e.g., "2024-03-20T15:30:00Z")

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
**None yet** - Frontend is blank slate (only Dockerfile exists)

### Integration Points
- **Backend API**: FastAPI running at `http://localhost:8000` via docker-compose
- **CORS**: Already configured in backend to allow `http://localhost:3000` (Next.js dev server)
- **Environment variables**: Backend URL should be configurable via `NEXT_PUBLIC_API_URL`

### Technical Context
- **Next.js 15**: Should use App Router (not Pages Router) per modern Next.js patterns
- **React 19**: Can use Server Components for initial data fetch, Client Components for interactive features (filters, sorting, modal)
- **TypeScript 5.5+**: Full type safety required
- **API response types**: Should mirror backend Pydantic schemas (LogResponse, LogListResponse)

### Established Patterns from Backend
- **Error responses**: `{"detail": "message", "request_id": "uuid"}` format
- **Validation errors**: HTTP 400 with structured error details
- **Severity enum**: INFO, WARNING, ERROR, CRITICAL (strict validation)
- **Cursor pagination**: Opaque base64-encoded tokens, no page numbers

</code_context>

<specifics>
## Specific Ideas

- **Infinite scroll + virtual scroll** chosen for best UX - smooth exploration without pagination clicks, plus performance optimization for large datasets
- **Modal for detail view** instead of separate route - preserves scroll position and filter context, feels faster
- **Filter sidebar** provides dedicated space for filters without cluttering the main table area - common in analytics/log tools
- **Filter chips above table** give immediate visibility into active filters and easy removal - important for investigating issues
- **URL state preservation** critical for sharing filtered views with team members ("check out these ERROR logs from yesterday")
- **Skeleton rows** feel more responsive than spinners - maintains layout and gives sense of content loading
- **Optimistic UI for create** makes form submission feel instant - important for good UX in demo
- **Borderless modern table** with colored severity badges emphasizes message content over visual clutter
- **Debounced search** provides instant feedback without hammering API - 300-500ms is sweet spot for feels-instant vs API efficiency

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 03-log-management-ui*
*Context gathered: 2026-03-21*
