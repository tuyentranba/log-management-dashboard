# Phase 4: Data Export - Research

**Researched:** 2026-03-22
**Domain:** CSV export with streaming response
**Confidence:** HIGH

## Summary

Phase 4 implements CSV export functionality for filtered log data using FastAPI's StreamingResponse to handle large datasets efficiently. The research confirms that FastAPI 0.135.1 supports streaming responses with async generators, Python's csv module handles RFC 4180 compliance with UTF-8-sig encoding for BOM, and SQLAlchemy 2.0's async streaming capabilities enable memory-efficient database result processing. Frontend download handling uses standard fetch API with blob conversion.

**Primary recommendation:** Use FastAPI StreamingResponse with async generator that yields CSV rows incrementally, combined with SQLAlchemy's stream() method and yield_per() for database-level streaming. Python's csv module with utf-8-sig encoding handles RFC 4180 compliance and Excel compatibility automatically.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Export Trigger UI:**
- Position above log table (near sort controls)
- Button displays "Export CSV" with download icon (lucide-react Download)
- Loading state: button disabled with spinner during export
- Button disabled when no logs match filters
- No log count shown in button text

**CSV Format:**
- Fields: timestamp, severity, source, message (id excluded)
- Headers: Title Case (Timestamp, Severity, Source, Message)
- Column order: Timestamp, Severity, Source, Message
- Timestamp format: ISO 8601 with timezone (e.g., 2025-03-22T14:30:00Z)
- Special characters: Standard CSV escaping (RFC 4180 compliant)
- Encoding: UTF-8 with BOM (Excel compatibility)

**Export Scope:**
- All filtered results (respects active filters from useLogFilters hook)
- Hard limit at 50,000 logs with error toast
- Sort order: Match current UI sort (WYSIWYG)
- Streaming: Backend uses FastAPI StreamingResponse

**User Feedback:**
- Success: Toast notification "CSV exported successfully"
- Error: Toast error message "Export failed: [reason]"
- Filename pattern: `logs-YYYY-MM-DD-HHMMSS.csv`
- Download: Browser native download (Content-Disposition: attachment header)

### Claude's Discretion
- Exact spinner animation during loading
- Toast duration and positioning details
- CSV library choice (Python csv module recommended)
- Error message wording for specific failure cases

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| EXPORT-01 | User can export filtered log data as CSV | FastAPI StreamingResponse + CSV module patterns |
| EXPORT-02 | CSV export uses streaming response (no memory loading) | SQLAlchemy async stream() + yield_per() for database streaming |
| EXPORT-03 | CSV export includes all log fields | CSV writer with explicit field ordering |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.135.1 | StreamingResponse class | Built-in streaming support, no additional dependencies |
| Python csv | stdlib | CSV generation | RFC 4180 compliant, utf-8-sig encoding built-in |
| SQLAlchemy | 2.0.48 | Async streaming queries | Native stream() and yield_per() for memory-efficient iteration |
| io.StringIO | stdlib | In-memory CSV buffering | Allows csv.writer to write to string buffer for streaming |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| anyio | Included with FastAPI | Event loop sleep in generators | Required in streaming generators for cancellation support |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Python csv | pandas.to_csv() | Pandas requires loading full dataset into memory (violates EXPORT-02) |
| StringIO buffer | Direct yield of strings | csv.writer handles RFC 4180 escaping automatically, manual is error-prone |
| SQLAlchemy stream() | Query.all() | all() loads entire result set into memory (violates EXPORT-02) |

**Installation:**
No new dependencies required — all libraries already in stack (FastAPI, SQLAlchemy, Python stdlib).

## Architecture Patterns

### Recommended Project Structure
```
backend/app/routers/
├── logs.py              # Add export endpoint here
backend/app/utils/
├── csv_export.py        # NEW: CSV generation utilities
backend/tests/
├── test_export.py       # NEW: Export endpoint tests
```

### Pattern 1: FastAPI Streaming CSV Endpoint
**What:** Endpoint that streams CSV rows using async generator
**When to use:** All CSV export scenarios with potentially large datasets
**Example:**
```python
# Source: FastAPI official docs + RFC 4180
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from datetime import datetime
import io
import csv
import anyio

router = APIRouter()

async def generate_csv_stream(logs_query):
    """
    Async generator that yields CSV rows incrementally.

    Prevents memory issues by streaming rows one at a time.
    """
    # Create StringIO buffer for csv.writer (in-memory)
    output = io.StringIO()

    # UTF-8 BOM for Excel compatibility (first yield only)
    yield '\ufeff'

    # Write CSV header
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Severity', 'Source', 'Message'])
    yield output.getvalue()
    output.truncate(0)
    output.seek(0)

    # Stream log rows from database
    async for log in logs_query:
        writer.writerow([
            log.timestamp.isoformat(),
            log.severity,
            log.source,
            log.message
        ])
        yield output.getvalue()
        output.truncate(0)
        output.seek(0)

        # Allow cancellation (required for proper streaming)
        await anyio.sleep(0)

@router.get("/api/export")
async def export_logs_csv(
    # Same filter parameters as list_logs endpoint
    severity: Optional[list[str]] = Query(None),
    source: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    sort: str = Query("timestamp", pattern="^(timestamp|severity|source)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    # Build query with same filtering logic as list_logs
    query = select(Log)
    # ... apply filters ...

    # Hard limit at 50,000 logs
    query = query.limit(50000)

    # Stream results from database
    result = await db.stream(query)
    logs_stream = result.scalars()

    # Generate filename with timestamp
    filename = f"logs-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.csv"

    return StreamingResponse(
        generate_csv_stream(logs_stream),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
```

### Pattern 2: SQLAlchemy Async Streaming with yield_per
**What:** Database streaming that fetches rows in batches instead of all at once
**When to use:** Queries returning 1000+ rows to avoid memory bloat
**Example:**
```python
# Source: SQLAlchemy 2.0 async docs
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def stream_logs(db: AsyncSession, filters: dict):
    """
    Stream log results from database using server-side cursor.

    yield_per controls batch size for memory efficiency.
    """
    query = select(Log)
    # ... apply filters ...

    # Use stream() for async iteration with server-side cursor
    result = await db.stream(
        query.execution_options(yield_per=1000)
    )

    # Async iteration processes rows incrementally
    async for log in result.scalars():
        yield log
```

**Key insight:** `yield_per(1000)` batches results in chunks of 1000 rows, preventing full result set loading into memory. The `stream()` method returns AsyncResult that supports async iteration.

### Pattern 3: Frontend File Download from Streaming Response
**What:** Download CSV file from streaming endpoint using fetch + blob
**When to use:** All client-side file download scenarios
**Example:**
```typescript
// Source: MDN Web Docs Fetch API + Blob
export async function exportLogs(filters: LogFilters): Promise<void> {
  const params = new URLSearchParams()
  // ... build params from filters ...

  const url = `${API_URL}/api/export?${params}`

  try {
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`Export failed: ${response.status}`)
    }

    // Convert streaming response to blob
    const blob = await response.blob()

    // Create object URL for download
    const downloadUrl = URL.createObjectURL(blob)

    // Trigger browser download
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = '' // Filename comes from Content-Disposition header
    document.body.appendChild(link)
    link.click()

    // Cleanup
    document.body.removeChild(link)
    URL.revokeObjectURL(downloadUrl)
  } catch (error) {
    throw new Error(`Export failed: ${error.message}`)
  }
}
```

### Pattern 4: CSV RFC 4180 Compliance with Python csv Module
**What:** Automatic escaping of special characters per RFC 4180 specification
**When to use:** All CSV generation to ensure Excel/Sheets compatibility
**Example:**
```python
# Source: Python csv docs + RFC 4180
import csv
import io

# utf-8-sig adds BOM automatically on first write
output = io.StringIO()
writer = csv.writer(output)

# csv.writer handles these cases automatically:
# - Fields with commas: wrapped in quotes
# - Fields with quotes: quotes doubled (escaped)
# - Fields with newlines: wrapped in quotes
# - Line terminators: CRLF (\r\n) by default

# Example data with special characters
writer.writerow([
    '2025-03-22T14:30:00Z',
    'ERROR',
    'api-server',
    'Database error: connection failed, retry in 5s'  # comma in message
])
writer.writerow([
    '2025-03-22T14:31:00Z',
    'INFO',
    'auth-service',
    'User said "hello world"'  # quotes in message
])

# Output is RFC 4180 compliant:
# 2025-03-22T14:30:00Z,ERROR,api-server,"Database error: connection failed, retry in 5s"
# 2025-03-22T14:31:00Z,INFO,auth-service,"User said ""hello world"""
```

**Key rules:**
- Fields with commas, quotes, or newlines are automatically wrapped in double quotes
- Internal double quotes are escaped by doubling them (`""`)
- Line terminators default to CRLF (`\r\n`)

### Anti-Patterns to Avoid
- **Loading all results then writing CSV:** Violates streaming requirement (EXPORT-02), causes memory issues at scale
- **Manual CSV escaping:** Error-prone, easy to miss edge cases like `\r\n` in messages or quote-in-quote scenarios
- **Using cursor pagination for export:** Adds complexity without benefit; streaming provides simpler solution
- **Omitting UTF-8 BOM:** Excel won't recognize UTF-8 encoding, displays garbled characters for non-ASCII text

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSV escaping | Manual quote/comma handling | Python csv.writer | Handles all RFC 4180 edge cases (nested quotes, CRLF in fields, delimiter escaping) |
| UTF-8 BOM | Manual `\xef\xbb\xbf` prefix | utf-8-sig encoding | Python stdlib handles BOM automatically, works with all file operations |
| Database streaming | Manual batch queries with OFFSET | SQLAlchemy stream() + yield_per() | Server-side cursors more efficient, handles transaction consistency |
| Async generator cancellation | Custom cancellation logic | anyio.sleep(0) in generator | FastAPI's cancellation protocol requires event loop yield points |

**Key insight:** CSV generation has many edge cases (quotes within quotes, multiline messages, delimiter conflicts). Python's csv module is battle-tested and RFC 4180 compliant. Manual implementations are bug-prone.

## Common Pitfalls

### Pitfall 1: Forgetting anyio.sleep(0) in Async Generator
**What goes wrong:** Streaming endpoint cannot be cancelled properly, continues processing even if client disconnects
**Why it happens:** Async generators need explicit yield points to event loop for cancellation handling
**How to avoid:** Add `await anyio.sleep(0)` inside generator loop (after each row yield)
**Warning signs:** Integration tests show cancelled requests continue processing, database queries run to completion after client disconnect

### Pitfall 2: Buffering Entire CSV Before Streaming
**What goes wrong:** Memory usage spikes with large exports, defeats streaming purpose
**Why it happens:** Accumulating all rows in a list/string before yielding to StreamingResponse
**How to avoid:** Yield CSV content incrementally (header first, then each row); use StringIO buffer that's cleared after each yield
**Warning signs:** Memory profiling shows linear growth with export size, OOM errors with 50k row exports

### Pitfall 3: Using .all() Instead of Async Iteration
**What goes wrong:** Database loads full result set into memory, negating streaming benefits
**Why it happens:** Force of habit from synchronous SQLAlchemy patterns
**How to avoid:** Use `await db.stream(query)` then `async for log in result.scalars()`; never call `.all()` on result
**Warning signs:** Database queries complete immediately (not progressively), memory usage proportional to result set size

### Pitfall 4: Incorrect Content-Disposition Header Format
**What goes wrong:** Browser doesn't recognize file as download, opens CSV in browser tab instead
**Why it happens:** Missing `attachment` directive or improper filename quoting
**How to avoid:** Use format `Content-Disposition: attachment; filename=<name>` (FastAPI StreamingResponse headers parameter)
**Warning signs:** CSV displays in browser instead of downloading, filename not preserved

### Pitfall 5: Not Handling 50k Limit Early
**What goes wrong:** Database queries 50k rows even when user expects error, wastes resources
**Why it happens:** Checking count after starting stream instead of in query construction
**How to avoid:** Add `.limit(50001)` to query, check if result count exceeds 50000 before starting stream (or rely on frontend validation)
**Warning signs:** Large exports take long time before showing error, backend logs show expensive count queries

### Pitfall 6: Missing UTF-8 BOM for Excel
**What goes wrong:** Excel displays garbled characters (mojibake) for non-ASCII text in exported CSV
**Why it happens:** Excel defaults to system encoding (Windows-1252) without BOM marker
**How to avoid:** Use utf-8-sig encoding OR yield `'\ufeff'` as first content in stream (BOM is U+FEFF)
**Warning signs:** Manual testing in Excel shows corrupted characters, users report unreadable exports

## Code Examples

Verified patterns from official sources:

### Complete Export Endpoint (Backend)
```python
# Source: FastAPI docs + SQLAlchemy 2.0 async docs
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from datetime import datetime
from typing import Optional, Annotated
import csv
import io
import anyio

from ..dependencies import get_db
from ..models import Log

router = APIRouter()

async def generate_csv_rows(logs_stream):
    """
    Async generator that yields CSV content incrementally.

    Args:
        logs_stream: AsyncResult.scalars() stream from SQLAlchemy

    Yields:
        str: CSV content chunks (header, then row by row)
    """
    # Create StringIO buffer for csv.writer
    output = io.StringIO()
    writer = csv.writer(output)

    # UTF-8 BOM for Excel compatibility
    yield '\ufeff'

    # Write header row
    writer.writerow(['Timestamp', 'Severity', 'Source', 'Message'])
    yield output.getvalue()
    output.truncate(0)
    output.seek(0)

    # Stream data rows
    async for log in logs_stream:
        writer.writerow([
            log.timestamp.isoformat(),  # ISO 8601 format
            log.severity,
            log.source,
            log.message
        ])
        yield output.getvalue()
        output.truncate(0)
        output.seek(0)

        # Allow cancellation (required for FastAPI streaming)
        await anyio.sleep(0)

@router.get("/api/export")
async def export_logs_csv(
    # Same filter parameters as list_logs endpoint
    severity: Annotated[Optional[list[str]], Query()] = None,
    source: Annotated[Optional[str], Query()] = None,
    date_from: Annotated[Optional[datetime], Query()] = None,
    date_to: Annotated[Optional[datetime], Query()] = None,
    sort: Annotated[str, Query(pattern="^(timestamp|severity|source)$")] = "timestamp",
    order: Annotated[str, Query(pattern="^(asc|desc)$")] = "desc",
    db: AsyncSession = Depends(get_db)
):
    """
    Export filtered logs as CSV with streaming response.

    Streams up to 50,000 logs matching current filters.
    Uses same filtering logic as list_logs endpoint.

    Returns:
        StreamingResponse with CSV content

    Raises:
        400: Invalid filter parameters
    """
    # Build query with same filtering logic as list_logs
    query = select(Log)

    # Apply filters (reuse validation logic)
    if severity:
        valid_severities = {"INFO", "WARNING", "ERROR", "CRITICAL"}
        for sev in severity:
            if sev not in valid_severities:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid severity: {sev}"
                )
        query = query.where(Log.severity.in_(severity))

    if source:
        query = query.where(Log.source.ilike(f"%{source}%"))

    if date_from:
        query = query.where(Log.timestamp >= date_from)

    if date_to:
        query = query.where(Log.timestamp <= date_to)

    # Apply sorting (match UI sort order)
    sort_column = getattr(Log, sort)
    if order == "desc":
        query = query.order_by(sort_column.desc(), Log.id.desc())
    else:
        query = query.order_by(sort_column.asc(), Log.id.asc())

    # Hard limit at 50,000 rows (requirement)
    query = query.limit(50000)

    # Stream results from database (yield_per for batch fetching)
    result = await db.stream(
        query.execution_options(yield_per=1000)
    )
    logs_stream = result.scalars()

    # Generate filename with timestamp
    filename = f"logs-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.csv"

    return StreamingResponse(
        generate_csv_rows(logs_stream),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
```

### Frontend Export Function
```typescript
// Source: MDN Web Docs Fetch API + Blob API
import { LogFilters } from './types'
import { API_URL } from './constants'

export async function exportLogs(filters: LogFilters): Promise<void> {
  const params = new URLSearchParams()

  // Build query parameters from filters
  if (filters.severity) {
    filters.severity.forEach(s => params.append('severity', s))
  }
  if (filters.source) params.append('source', filters.source)
  if (filters.date_from) params.append('date_from', filters.date_from)
  if (filters.date_to) params.append('date_to', filters.date_to)
  if (filters.sort) params.append('sort', filters.sort)
  if (filters.order) params.append('order', filters.order)

  const url = `${API_URL}/api/export?${params}`

  const response = await fetch(url)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Export failed: ${response.status}`)
  }

  // Convert streaming response to blob
  const blob = await response.blob()

  // Extract filename from Content-Disposition header
  const contentDisposition = response.headers.get('Content-Disposition')
  let filename = 'logs.csv'
  if (contentDisposition) {
    const matches = /filename=([^;]+)/.exec(contentDisposition)
    if (matches?.[1]) {
      filename = matches[1].trim()
    }
  }

  // Create object URL and trigger download
  const downloadUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()

  // Cleanup
  document.body.removeChild(link)
  URL.revokeObjectURL(downloadUrl)
}
```

### Export Button Component
```tsx
// Source: shadcn/ui Button + lucide-react icons
'use client'

import { useState } from 'react'
import { Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/use-toast'
import { exportLogs } from '@/lib/api'
import { LogFilters } from '@/lib/types'

interface ExportButtonProps {
  filters: LogFilters
  disabled?: boolean  // Disable when no logs match filters
}

export function ExportButton({ filters, disabled }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false)
  const { toast } = useToast()

  const handleExport = async () => {
    setIsExporting(true)

    try {
      await exportLogs(filters)
      toast({
        title: "CSV exported successfully",
        description: "Your file has been downloaded"
      })
    } catch (error) {
      toast({
        title: "Export failed",
        description: error.message,
        variant: "destructive"
      })
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <Button
      onClick={handleExport}
      disabled={disabled || isExporting}
      variant="outline"
    >
      <Download className="mr-2 h-4 w-4" />
      {isExporting ? 'Exporting...' : 'Export CSV'}
    </Button>
  )
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Synchronous StreamingResponse | Async generator required | FastAPI 0.60+ (2020) | Must use async def with await for proper cancellation |
| SQLAlchemy Query.yield_per() | AsyncSession.stream() + yield_per | SQLAlchemy 2.0 (2023) | Async-native streaming, server-side cursors by default |
| Manual BOM bytes | utf-8-sig encoding | Python 3.x stdlib | Cleaner API, works with all file operations |
| FileResponse for exports | StreamingResponse | FastAPI 0.50+ (2020) | Streaming prevents memory issues with large files |

**Deprecated/outdated:**
- **synchronous generators in StreamingResponse:** FastAPI now requires async generators for proper cancellation handling (use `async def` with `yield`)
- **Query.yield_per() in async context:** SQLAlchemy 2.0 uses `stream()` method instead; yield_per is now an execution option
- **Manual UTF-8 BOM handling:** Python's utf-8-sig encoding handles BOM automatically, no need for manual `\xef\xbb\xbf` prefixing

## Open Questions

1. **Should we validate 50k limit before or during streaming?**
   - What we know: Can add LIMIT 50001 to query and check count during iteration
   - What's unclear: Performance trade-off between count query upfront vs. checking during stream
   - Recommendation: Use query LIMIT 50000 (database enforces), no separate count query (avoids extra work)

2. **Should CSV include log ID column?**
   - What we know: CONTEXT.md specifies "id field excluded for cleaner analysis"
   - What's unclear: None — decision is locked
   - Recommendation: Follow CONTEXT.md decision (no ID column)

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 + pytest-asyncio 1.3.0 |
| Config file | none — using defaults (tests/ directory autodiscovery) |
| Quick run command | `pytest backend/tests/test_export.py -x -v` |
| Full suite command | `pytest backend/tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| EXPORT-01 | Export filtered logs as CSV with proper headers/format | integration | `pytest backend/tests/test_export.py::test_export_csv_format -x` | ❌ Wave 0 |
| EXPORT-01 | Export respects all filter parameters (severity, source, date range) | integration | `pytest backend/tests/test_export.py::test_export_with_filters -x` | ❌ Wave 0 |
| EXPORT-01 | Export respects sort order (matches UI) | integration | `pytest backend/tests/test_export.py::test_export_sort_order -x` | ❌ Wave 0 |
| EXPORT-02 | Export streams response (validates StreamingResponse type) | unit | `pytest backend/tests/test_export.py::test_export_returns_streaming_response -x` | ❌ Wave 0 |
| EXPORT-02 | Export handles 50k row limit without memory issues | integration | `pytest backend/tests/test_export.py::test_export_large_dataset -x` | ❌ Wave 0 |
| EXPORT-03 | CSV includes all required fields (timestamp, severity, source, message) | integration | `pytest backend/tests/test_export.py::test_export_csv_fields -x` | ❌ Wave 0 |
| EXPORT-03 | CSV uses correct field order and Title Case headers | integration | `pytest backend/tests/test_export.py::test_export_csv_headers -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest backend/tests/test_export.py -x -v`
- **Per wave merge:** `pytest backend/tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `backend/tests/test_export.py` — covers all EXPORT-* requirements (7 test cases)
- [ ] Existing `conftest.py` provides test fixtures — no framework gaps

## Sources

### Primary (HIGH confidence)
- FastAPI official docs (https://fastapi.tiangolo.com/advanced/custom-response/) - StreamingResponse usage, headers, async generators
- Python stdlib docs (https://docs.python.org/3/library/csv.html) - csv.writer, RFC 4180 compliance
- Python stdlib docs (https://docs.python.org/3/library/codecs.html) - utf-8-sig encoding for BOM
- SQLAlchemy 2.0 docs (https://docs.sqlalchemy.org/en/20/orm/queryguide/api.html) - yield_per() batching
- SQLAlchemy 2.0 async docs (https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) - AsyncSession.stream() method

### Secondary (MEDIUM confidence)
- MDN Web Docs (https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch) - Fetch API streaming responses
- MDN Web Docs (https://developer.mozilla.org/en-US/docs/Web/API/Blob) - Blob API for file downloads
- RFC 4180 (https://www.rfc-editor.org/rfc/rfc4180) - CSV format specification

### Tertiary (LOW confidence)
None — all findings verified with official documentation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already in project (FastAPI 0.135.1, SQLAlchemy 2.0.48, Python stdlib)
- Architecture: HIGH - Patterns verified from official FastAPI and SQLAlchemy 2.0 documentation
- Pitfalls: HIGH - Specific edge cases documented in official sources (anyio.sleep for cancellation, utf-8-sig for BOM)

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (30 days — stack is mature, low churn rate)
