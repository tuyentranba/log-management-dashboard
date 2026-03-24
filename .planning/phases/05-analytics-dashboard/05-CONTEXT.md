# Phase 5: Analytics Dashboard - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Visualize aggregated log metrics through an analytics dashboard with time-series charts and severity distribution. Users can filter by date range, severity, and source to analyze log patterns. The dashboard displays summary statistics and interactive charts showing log volume trends and severity breakdown.

**In scope:** Analytics view, summary stats, time-series chart, severity distribution chart, date range filtering
**Out of scope:** Real-time updates (separate phase), caching (separate phase), advanced analytics (anomaly detection, correlation)

</domain>

<decisions>
## Implementation Decisions

### Chart Library
- **Library:** Recharts - React-first declarative API, good TypeScript support, works with Next.js SSR
- **Time-series chart type:** Area chart (filled area under line) - visually prominent for volume data
- **Severity distribution chart type:** Bar chart (vertical bars) - clear categorical comparison
- **Color scheme:** Use same vibrant severity colors from log list (blue-500 for INFO, yellow-500 for WARNING, orange-600 for ERROR, red-600 for CRITICAL) - consistency across UI

### Dashboard Layout
- **Layout structure:** Summary stat cards in horizontal row at top, charts in 2-column grid below
- **Responsive behavior:** Single column on mobile/tablet, 2-column grid on desktop
- **Stat card content:** Count + label only (e.g., "15,234" with "Total Logs" label) - simple, clean
- **Stat scope:** Show filtered subset only - stats reflect active filters (date range, severity, source)
- **Navigation:** "View All Logs" button in top right to jump to /logs page

### Time Granularity
- **Bucket strategy:** Auto-adjust based on date range
  - Hourly buckets for ranges <3 days
  - Daily buckets for 3-30 days
  - Weekly buckets for >30 days
- **Date range selection:** Presets + custom date picker
- **Date presets:** Last hour, Last 6 hours, Last 24 hours, Last 7 days, Last 30 days
- **Default range:** Last 7 days (on initial page load)
- **Timezone handling:** Display dates in user's local timezone, but send UTC to backend (follows Phase 1 UTC-normalized pattern)

### Chart Interactivity
- **Time-series click behavior:** Show tooltip only (hover shows count, click does nothing)
- **Severity bar click behavior:** Navigate to /logs page with that severity pre-selected in filters
- **Tooltip content:**
  - Time-series: Date/time bucket + log count
  - Severity chart: Severity level + count + percentage of total
- **Charts update when:** User changes date range, severity filter, or source filter

### API Design
- **Endpoint:** GET /api/analytics
- **Required parameter:** date_from and date_to (enforces ANALYTICS-06 - no unbounded COUNT queries)
- **Optional parameters:** severity (multi-select), source
- **Response schema:** JSON with summary stats + time-series data + severity distribution data
- **Error handling:** 400 if date range missing, follows Phase 2 error conventions

### Claude's Discretion
- Exact Recharts component props (margin, padding, axis formatting)
- Loading skeleton design for charts
- Chart animation timing/easing
- Hover tooltip styling details
- Empty state message when no logs match filters
- Error state handling for API failures

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — Analytics requirements (ANALYTICS-01 through ANALYTICS-07), UI-04, timezone handling constraints
- `.planning/ROADMAP.md` §Phase 5 — Success criteria, performance targets (<2s load time with 100k logs)

### Prior decisions
- `.planning/STATE.md` §Key Decisions — UTC normalization, BRIN indexes, composite indexes
- `.planning/phases/03-log-management-ui/` — Frontend patterns, URL state management with nuqs, severity colors
- `.planning/phases/01-foundation-database/` — Database schema, indexes, timestamp handling
- `.planning/phases/02-core-api-layer/` — API conventions, error handling, Pydantic schemas

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/hooks/use-log-filters.ts` — URL state management hook (can create similar `use-analytics-filters.ts`)
- `frontend/src/lib/constants.ts` — SEVERITY_COLORS constant for chart colors
- `frontend/src/components/shared/severity-badge.tsx` — Severity display patterns
- `frontend/src/lib/api.ts` — API client patterns (add `fetchAnalytics` function)
- `frontend/src/lib/types.ts` — Type definitions (add AnalyticsResponse type)

### Established Patterns
- **Frontend:** Next.js 15 App Router, Server Components for SSR + Client Components for interactivity
- **UI:** shadcn/ui components + Tailwind CSS, responsive grid with `grid-cols-1 md:grid-cols-2`
- **State:** nuqs for URL state persistence (filters should persist in URL)
- **Backend:** FastAPI async endpoints, SQLAlchemy 2.0 with async session
- **Queries:** Use existing composite index on (timestamp, severity, source) for filtering
- **Aggregations:** PostgreSQL date_trunc() for time bucketing, GROUP BY for counting

### Integration Points
- **Frontend:** New `/analytics` page under `frontend/src/app/analytics/page.tsx`
- **Backend:** New router `backend/app/routers/analytics.py` registered in `main.py`
- **Navigation:** Add "Analytics" link to main navigation (alongside "Logs" and "Create")
- **Navigation flow:** Analytics → click severity bar → /logs with pre-filled severity filter

### New Dependencies
- **Frontend:** `recharts` (install via npm) - charting library
- **Frontend:** `date-fns` (already installed) - date formatting for tooltips
- **Backend:** No new dependencies (use existing SQLAlchemy, Pydantic, FastAPI)

</code_context>

<specifics>
## Specific Ideas

- Date range presets should be quick-access buttons (not dropdown) - faster interaction
- Time-series chart should fill width, severity chart can be narrower (60% width on desktop)
- Stat cards should use subtle background colors matching severity (very light tints of severity colors)
- Loading state should show skeleton cards + skeleton charts (not full-page spinner)
- When navigating from severity bar click to /logs, open in same tab (not new tab) - feels like drilling down not jumping away

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 05-analytics-dashboard*
*Context gathered: 2026-03-23*
