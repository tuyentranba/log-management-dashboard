# Phase 4: Data Export - Context

**Gathered:** 2025-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

CSV export of filtered log data from the log list page. Users can download all logs matching their current filters (date range, severity, source, search text) as a CSV file. Streaming export handles large datasets without memory issues.

</domain>

<decisions>
## Implementation Decisions

### Export Trigger UI
- Position above log table (near sort controls) for prominence
- Button displays "Export CSV" with download icon (lucide-react Download)
- Loading state: button disabled with spinner during export
- Button disabled when no logs match filters (prevents empty exports)
- No log count shown in button text (keeps UI simple)

### CSV Format
- **Fields included**: timestamp, severity, source, message (id field excluded for cleaner analysis)
- **Headers**: Title Case format (Timestamp, Severity, Source, Message) — Excel-friendly
- **Column order**: Timestamp, Severity, Source, Message (chronological flow)
- **Timestamp format**: ISO 8601 with timezone (e.g., 2025-03-22T14:30:00Z) — machine-readable, sortable
- **Special characters**: Standard CSV escaping — messages with newlines/commas wrapped in quotes, internal quotes escaped (RFC 4180 compliant)
- **Encoding**: UTF-8 with BOM (Excel compatibility)

### Export Scope
- **Scope**: All filtered results (respects active filters from useLogFilters hook)
- **Size limit**: Hard limit at 50,000 logs — show error toast "Export limited to 50,000 logs. Please apply additional filters."
- **Sort order**: Match current UI sort (WYSIWYG) — if user sorted by severity DESC, CSV exports in that order
- **Streaming**: Backend uses FastAPI StreamingResponse (EXPORT-02 requirement) — no memory loading of full dataset

### User Feedback
- **Success**: Toast notification "CSV exported successfully" with checkmark — matches Phase 3 pattern (Sonner toast)
- **Error**: Toast error message "Export failed: [reason]" in red — consistent with existing error handling
- **Filename pattern**: `logs-YYYY-MM-DD-HHMMSS.csv` (e.g., logs-2025-03-22-143045.csv) — unique for multiple exports same day
- **Download**: Browser native download (Content-Disposition: attachment header)

### Claude's Discretion
- Exact spinner animation during loading
- Toast duration and positioning details
- CSV library choice (Python csv module recommended)
- Error message wording for specific failure cases

</decisions>

<canonical_refs>
## Canonical References

No external specs — requirements fully captured in decisions above.

**Requirements addressed:**
- EXPORT-01: User can export filtered log data as CSV
- EXPORT-02: CSV export uses streaming response (no memory loading)
- EXPORT-03: CSV export includes all log fields (timestamp, severity, source, message)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Filter state**: `useLogFilters` hook provides current filter state (search, severity, source, date_from, date_to, sort, order)
- **Button component**: shadcn/ui Button with variants and loading states
- **Toast notifications**: Sonner toast already integrated in layout (top-right, rich colors)
- **Icons**: lucide-react library available (Download icon)

### Established Patterns
- **Filter URL persistence**: nuqs library maintains filter state in URL (Phase 3)
- **API filtering**: Backend logs endpoint supports all filter parameters (Phase 2)
- **Error handling**: Toast notifications for errors (Phase 3 pattern)
- **Loading states**: Button disabled with spinner (Phase 3 pattern)

### Integration Points
- **Backend**: New GET /api/export endpoint in `backend/app/routers/logs.py`
- **Frontend**: Export button component in log list page (`frontend/src/app/logs/page.tsx`)
- **API client**: New `exportLogs` function in `frontend/src/lib/api.ts`

</code_context>

<specifics>
## Specific Ideas

- CSV should work well with Excel and Google Sheets (hence UTF-8 with BOM and Title Case headers)
- Export respects user's view — if they sorted by severity, CSV should match that order (WYSIWYG principle)
- 50k limit prevents accidental huge exports while handling realistic use cases (requirement specifies 10k test case)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-data-export*
*Context gathered: 2025-03-22*
