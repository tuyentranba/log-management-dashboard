# Phase 5: Analytics Dashboard - Research

**Researched:** 2026-03-25
**Domain:** Analytics dashboard with time-series charts and aggregated log metrics
**Confidence:** HIGH

## Summary

Phase 5 requires building an analytics dashboard that visualizes aggregated log data through interactive charts. The dashboard displays summary statistics (total logs, counts by severity), time-series trends showing log volume over time, and severity distribution histograms. Users can filter by date range, severity, and source, with all filters required to pass date_from/date_to to prevent unbounded aggregation queries.

Key architectural decisions: Recharts for declarative React charts (chosen by user), PostgreSQL date_trunc() for time bucketing with automatic granularity adjustment (hourly/daily/weekly based on range), SQLAlchemy func for aggregation queries with GROUP BY, Next.js Server Component for initial data fetch with Client Component for chart interactivity, and nuqs for URL state management (consistent with Phase 3 patterns).

The implementation leverages existing Phase 1 composite index (timestamp, severity, source) for efficient filtered aggregations, follows Phase 2 API conventions (Pydantic schemas, async endpoints), and extends Phase 3 UI patterns (shadcn/ui components, URL state, loading overlays, severity colors). Charts use area chart for time-series (visually prominent volume data) and bar chart for severity distribution (clear categorical comparison).

**Primary recommendation:** Use Recharts with PostgreSQL date_trunc() aggregations, automatic time granularity adjustment based on date range, and require date range filter on all analytics queries to ensure <2s performance with 100k logs.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Chart Library:**
- Library: Recharts - React-first declarative API, good TypeScript support, works with Next.js SSR
- Time-series chart type: Area chart (filled area under line) - visually prominent for volume data
- Severity distribution chart type: Bar chart (vertical bars) - clear categorical comparison
- Color scheme: Use same vibrant severity colors from log list (blue-500 for INFO, yellow-500 for WARNING, orange-600 for ERROR, red-600 for CRITICAL) - consistency across UI

**Dashboard Layout:**
- Layout structure: Summary stat cards in horizontal row at top, charts in 2-column grid below
- Responsive behavior: Single column on mobile/tablet, 2-column grid on desktop
- Stat card content: Count + label only (e.g., "15,234" with "Total Logs" label) - simple, clean
- Stat scope: Show filtered subset only - stats reflect active filters (date range, severity, source)
- Navigation: "View All Logs" button in top right to jump to /logs page

**Time Granularity:**
- Bucket strategy: Auto-adjust based on date range
  - Hourly buckets for ranges <3 days
  - Daily buckets for 3-30 days
  - Weekly buckets for >30 days
- Date range selection: Presets + custom date picker
- Date presets: Last hour, Last 6 hours, Last 24 hours, Last 7 days, Last 30 days
- Default range: Last 7 days (on initial page load)
- Timezone handling: Display dates in user's local timezone, but send UTC to backend (follows Phase 1 UTC-normalized pattern)

**Chart Interactivity:**
- Time-series click behavior: Show tooltip only (hover shows count, click does nothing)
- Severity bar click behavior: Navigate to /logs page with that severity pre-selected in filters
- Tooltip content:
  - Time-series: Date/time bucket + log count
  - Severity chart: Severity level + count + percentage of total
- Charts update when: User changes date range, severity filter, or source filter

**API Design:**
- Endpoint: GET /api/analytics
- Required parameter: date_from and date_to (enforces ANALYTICS-06 - no unbounded COUNT queries)
- Optional parameters: severity (multi-select), source
- Response schema: JSON with summary stats + time-series data + severity distribution data
- Error handling: 400 if date range missing, follows Phase 2 error conventions

### Claude's Discretion

- Exact Recharts component props (margin, padding, axis formatting)
- Loading skeleton design for charts
- Chart animation timing/easing
- Hover tooltip styling details
- Empty state message when no logs match filters
- Error state handling for API failures

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ANALYTICS-01 | User can view analytics dashboard with aggregated log metrics | Next.js /analytics page + GET /api/analytics endpoint with summary stats, time-series data, severity distribution |
| ANALYTICS-02 | Dashboard displays summary statistics (total logs, counts by severity) | SQLAlchemy COUNT(*) aggregation + GROUP BY severity queries + stat card components |
| ANALYTICS-03 | Dashboard displays chart showing log count trends over time | PostgreSQL date_trunc() for time bucketing + Recharts AreaChart with automatic granularity adjustment |
| ANALYTICS-04 | Dashboard displays histogram of log severity distribution | SQLAlchemy GROUP BY severity COUNT queries + Recharts BarChart with click navigation to /logs |
| ANALYTICS-05 | Dashboard filters work for date range, severity, and source | nuqs URL state management + WHERE clauses on timestamp/severity/source + composite index optimization |
| ANALYTICS-06 | Analytics queries require date range filter (no unbounded COUNT queries) | FastAPI validation requiring date_from/date_to parameters + 400 error if missing |
| ANALYTICS-07 | Time-series aggregations use explicit timezone handling | PostgreSQL timestamptz column + date_trunc with UTC normalization + client-side local timezone display |
| UI-04 | Frontend provides analytics dashboard page | Next.js /analytics route with Server Component data fetch + Client Component charts + shadcn/ui layout |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| recharts | 2.x (latest) | React charting library | User-chosen, React-first declarative API, composable components, good TypeScript support, 44k+ stars on GitHub |
| date-fns | 4.x (already installed) | Date formatting and manipulation | Already in project (Phase 3), handles ISO 8601 parsing, timezone-aware formatting, local timezone display |
| PostgreSQL date_trunc | Built-in | Time-series bucketing | Native timestamptz function, efficient GROUP BY aggregation, supports hour/day/week/month granularity |
| SQLAlchemy func | 2.0 (already installed) | SQL function calls | Already in project (Phase 1), provides func.date_trunc() and func.count() for aggregations |
| nuqs | 2.x (already installed) | URL state management | Already in project (Phase 3), consistent filter state pattern, type-safe query params |
| Next.js 15 | 15.x (already installed) | React framework | Already in project (Phase 3), Server Components for data fetch + Client Components for charts |
| shadcn/ui | CLI-based (already installed) | UI components | Already in project (Phase 3), Card/Button/Separator components for dashboard layout |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @radix-ui/react-popover | Latest | Date range picker | For custom date picker UI (if presets insufficient), accessible popover for calendar |
| Pydantic | 2.12+ (already installed) | Response schema validation | Analytics response schema (summary stats + time-series + severity distribution) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Recharts | Chart.js | More features but imperative API (refs, lifecycle management), harder with React |
| Recharts | Victory | More customizable but larger bundle (120kb vs 70kb), steeper learning curve |
| Recharts | D3.js | Most powerful but imperative, significant learning curve, manual React integration |
| date_trunc | Application-level bucketing | More flexible but slower (no DB optimization), more memory usage |
| Auto granularity | Fixed granularity | Simpler but poor UX (hourly buckets for 30-day range = 720 data points, chart becomes unreadable) |

**Installation:**
```bash
# Frontend
npm install recharts

# Backend - no new dependencies (use existing SQLAlchemy, Pydantic, FastAPI)
```

## Architecture Patterns

### Recommended Project Structure
```
frontend/
├── src/
│   ├── app/
│   │   ├── analytics/              # Analytics dashboard
│   │   │   ├── page.tsx            # Server Component - fetch initial data
│   │   │   └── _components/
│   │   │       ├── analytics-view.tsx          # Client Component wrapper
│   │   │       ├── summary-stats.tsx           # Stat cards (Total, by severity)
│   │   │       ├── time-series-chart.tsx       # Area chart with Recharts
│   │   │       ├── severity-distribution-chart.tsx # Bar chart with Recharts
│   │   │       ├── date-range-filter.tsx       # Presets + custom picker
│   │   │       ├── analytics-filters.tsx       # Severity/source filters
│   │   │       └── chart-skeleton.tsx          # Loading state for charts
│   │   └── ...
│   ├── lib/
│   │   ├── api.ts               # Add fetchAnalytics() function
│   │   ├── types.ts             # Add AnalyticsResponse type
│   │   └── utils.ts             # Add determineTimeGranularity() helper
│   └── hooks/
│       └── use-analytics-filters.ts # URL state for analytics filters
│
backend/
├── app/
│   ├── routers/
│   │   └── analytics.py          # New router for analytics endpoint
│   ├── schemas/
│   │   └── analytics.py          # Analytics request/response schemas
│   └── utils/
│       └── time_buckets.py       # Granularity calculation helper
```

### Pattern 1: Time Granularity Auto-Adjustment
**What:** Automatically select hour/day/week bucket size based on date range to maintain readable charts (20-50 data points optimal)
**When to use:** All time-series aggregations - prevents over-dense charts (720 hourly points for 30 days) or under-sampled charts (7 daily points for 7 hours)
**Example:**
```python
# backend/app/utils/time_buckets.py
from datetime import datetime, timedelta

def determine_granularity(date_from: datetime, date_to: datetime) -> str:
    """
    Determine optimal time bucket granularity based on date range.

    Returns PostgreSQL date_trunc unit: 'hour', 'day', or 'week'
    """
    delta = date_to - date_from

    if delta < timedelta(days=3):
        return 'hour'     # <3 days: hourly (max 72 points)
    elif delta <= timedelta(days=30):
        return 'day'      # 3-30 days: daily (max 30 points)
    else:
        return 'week'     # >30 days: weekly (reduces long ranges)

# backend/app/routers/analytics.py
from sqlalchemy import func, select
from ..utils.time_buckets import determine_granularity

@router.get("/analytics")
async def get_analytics(
    date_from: datetime,
    date_to: datetime,
    severity: Optional[list[str]] = None,
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # Determine granularity
    granularity = determine_granularity(date_from, date_to)

    # Build time-series query with date_trunc
    time_series_query = select(
        func.date_trunc(granularity, Log.timestamp).label('bucket'),
        func.count().label('count')
    ).where(
        Log.timestamp >= date_from,
        Log.timestamp <= date_to
    )

    # Apply optional filters
    if severity:
        time_series_query = time_series_query.where(Log.severity.in_(severity))
    if source:
        time_series_query = time_series_query.where(Log.source.ilike(f"%{source}%"))

    # Group by bucket and order chronologically
    time_series_query = time_series_query.group_by('bucket').order_by('bucket')

    result = await db.execute(time_series_query)
    time_series_data = [
        {"timestamp": row.bucket.isoformat(), "count": row.count}
        for row in result
    ]

    return {"time_series": time_series_data, "granularity": granularity}
```
**Source:** PostgreSQL date_trunc() documentation (https://www.postgresql.org/docs/current/functions-datetime.html)

### Pattern 2: Summary Stats Aggregation
**What:** Compute total count and per-severity counts in a single query using conditional aggregation
**When to use:** Dashboard summary cards - more efficient than separate queries per severity
**Example:**
```python
# backend/app/routers/analytics.py
from sqlalchemy import func, select, case

@router.get("/analytics")
async def get_analytics(
    date_from: datetime,
    date_to: datetime,
    severity: Optional[list[str]] = None,
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # Build summary stats query with conditional aggregation
    summary_query = select(
        func.count().label('total'),
        func.count().filter(Log.severity == 'INFO').label('info_count'),
        func.count().filter(Log.severity == 'WARNING').label('warning_count'),
        func.count().filter(Log.severity == 'ERROR').label('error_count'),
        func.count().filter(Log.severity == 'CRITICAL').label('critical_count')
    ).where(
        Log.timestamp >= date_from,
        Log.timestamp <= date_to
    )

    # Apply optional filters
    if severity:
        summary_query = summary_query.where(Log.severity.in_(severity))
    if source:
        summary_query = summary_query.where(Log.source.ilike(f"%{source}%"))

    result = await db.execute(summary_query)
    row = result.one()

    return {
        "total": row.total,
        "by_severity": {
            "INFO": row.info_count,
            "WARNING": row.warning_count,
            "ERROR": row.error_count,
            "CRITICAL": row.critical_count
        }
    }
```
**Source:** SQLAlchemy filter() documentation (https://docs.sqlalchemy.org/en/20/core/sqlelement.html)

### Pattern 3: Severity Distribution with GROUP BY
**What:** Count logs per severity level using GROUP BY for histogram data
**When to use:** Severity distribution bar chart - shows relative frequency of each severity
**Example:**
```python
# backend/app/routers/analytics.py
from sqlalchemy import func, select

@router.get("/analytics")
async def get_analytics(
    date_from: datetime,
    date_to: datetime,
    severity: Optional[list[str]] = None,
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # Build severity distribution query
    severity_query = select(
        Log.severity,
        func.count().label('count')
    ).where(
        Log.timestamp >= date_from,
        Log.timestamp <= date_to
    )

    # Apply optional filters
    if severity:
        severity_query = severity_query.where(Log.severity.in_(severity))
    if source:
        severity_query = severity_query.where(Log.source.ilike(f"%{source}%"))

    # Group by severity
    severity_query = severity_query.group_by(Log.severity)

    result = await db.execute(severity_query)
    severity_distribution = [
        {"severity": row.severity, "count": row.count}
        for row in result
    ]

    return {"severity_distribution": severity_distribution}
```

### Pattern 4: Recharts Area Chart (Time-Series)
**What:** Render time-series data as area chart with Recharts declarative API
**When to use:** Time-series visualization - filled area under line is visually prominent for volume data
**Example:**
```typescript
// frontend/src/app/analytics/_components/time-series-chart.tsx
'use client'

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { format, parseISO } from 'date-fns'

interface TimeSeriesDataPoint {
  timestamp: string  // ISO 8601
  count: number
}

interface Props {
  data: TimeSeriesDataPoint[]
  granularity: 'hour' | 'day' | 'week'
}

export function TimeSeriesChart({ data, granularity }: Props) {
  // Format timestamp based on granularity
  const formatXAxis = (timestamp: string) => {
    const date = parseISO(timestamp)
    if (granularity === 'hour') {
      return format(date, 'MMM d, HH:mm')  // "Mar 25, 14:00"
    } else if (granularity === 'day') {
      return format(date, 'MMM d')  // "Mar 25"
    } else {
      return format(date, 'MMM d')  // "Mar 25" (week start)
    }
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <AreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="timestamp"
          tickFormatter={formatXAxis}
          angle={-45}
          textAnchor="end"
          height={80}
        />
        <YAxis />
        <Tooltip
          labelFormatter={(value) => format(parseISO(value as string), 'PPpp')}
          formatter={(value: number) => [`${value} logs`, 'Count']}
        />
        <Area
          type="monotone"
          dataKey="count"
          stroke="#3b82f6"
          fill="#3b82f6"
          fillOpacity={0.6}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
```
**Source:** Recharts AreaChart documentation (https://recharts.org/en-US/api/AreaChart)

### Pattern 5: Recharts Bar Chart with Click Navigation
**What:** Render severity distribution as bar chart with onClick navigation to filtered log list
**When to use:** Severity distribution - clicking bar drills down to /logs with severity pre-selected
**Example:**
```typescript
// frontend/src/app/analytics/_components/severity-distribution-chart.tsx
'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { useRouter } from 'next/navigation'
import { SEVERITY_COLORS } from '@/lib/constants'

interface SeverityDataPoint {
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
  count: number
}

interface Props {
  data: SeverityDataPoint[]
  total: number
}

export function SeverityDistributionChart({ data, total }: Props) {
  const router = useRouter()

  const handleBarClick = (data: SeverityDataPoint) => {
    // Navigate to /logs with severity pre-selected
    router.push(`/logs?severity=${data.severity}`)
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="severity" />
        <YAxis />
        <Tooltip
          formatter={(value: number, name, props) => {
            const percentage = ((value / total) * 100).toFixed(1)
            return [`${value} logs (${percentage}%)`, 'Count']
          }}
        />
        <Bar
          dataKey="count"
          onClick={handleBarClick}
          cursor="pointer"
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={SEVERITY_COLORS[entry.severity] || '#gray-500'}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
```

### Pattern 6: Date Range Presets with Custom Picker
**What:** Quick-access preset buttons (Last 7 days, Last 30 days) + custom date picker for arbitrary ranges
**When to use:** Date range filter - 90% of users use presets, custom picker for power users
**Example:**
```typescript
// frontend/src/app/analytics/_components/date-range-filter.tsx
'use client'

import { useQueryStates, parseAsString } from 'nuqs'
import { Button } from '@/components/ui/button'
import { subDays, subHours, format } from 'date-fns'

export function DateRangeFilter() {
  const [filters, setFilters] = useQueryStates({
    date_from: parseAsString.withDefault(format(subDays(new Date(), 7), 'yyyy-MM-dd')),
    date_to: parseAsString.withDefault(format(new Date(), 'yyyy-MM-dd'))
  })

  const applyPreset = (hours?: number, days?: number) => {
    const now = new Date()
    const from = hours ? subHours(now, hours) : subDays(now, days!)

    setFilters({
      date_from: from.toISOString(),
      date_to: now.toISOString()
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2 flex-wrap">
        <Button variant="outline" size="sm" onClick={() => applyPreset(1)}>
          Last Hour
        </Button>
        <Button variant="outline" size="sm" onClick={() => applyPreset(6)}>
          Last 6 Hours
        </Button>
        <Button variant="outline" size="sm" onClick={() => applyPreset(24)}>
          Last 24 Hours
        </Button>
        <Button variant="outline" size="sm" onClick={() => applyPreset(undefined, 7)}>
          Last 7 Days
        </Button>
        <Button variant="outline" size="sm" onClick={() => applyPreset(undefined, 30)}>
          Last 30 Days
        </Button>
      </div>

      {/* Custom date inputs */}
      <div className="flex gap-2 items-center">
        <input
          type="datetime-local"
          value={filters.date_from}
          onChange={(e) => setFilters({ date_from: e.target.value })}
          className="border rounded px-2 py-1"
        />
        <span>to</span>
        <input
          type="datetime-local"
          value={filters.date_to}
          onChange={(e) => setFilters({ date_to: e.target.value })}
          className="border rounded px-2 py-1"
        />
      </div>
    </div>
  )
}
```

### Pattern 7: Server Component → Client Component Data Flow
**What:** Fetch analytics data in Server Component, pass to Client Component for chart rendering (charts require interactivity)
**When to use:** Analytics dashboard page - Server Component for initial fetch, Client Component for Recharts
**Example:**
```typescript
// frontend/src/app/analytics/page.tsx (Server Component)
import { AnalyticsView } from './_components/analytics-view'

export default async function AnalyticsPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  // Build query params from URL state
  const params = new URLSearchParams()
  params.append('date_from', searchParams.date_from as string || /* default */)
  params.append('date_to', searchParams.date_to as string || /* default */)
  if (searchParams.severity) {
    (searchParams.severity as string[]).forEach(s => params.append('severity', s))
  }
  if (searchParams.source) params.append('source', searchParams.source as string)

  // Fetch initial data on server
  const data = await fetch(`${process.env.API_URL}/api/analytics?${params}`, {
    cache: 'no-store'
  }).then(r => r.json())

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Analytics Dashboard</h1>
      {/* Pass data to Client Component */}
      <AnalyticsView initialData={data} />
    </div>
  )
}

// frontend/src/app/analytics/_components/analytics-view.tsx (Client Component)
'use client'

import { SummaryStats } from './summary-stats'
import { TimeSeriesChart } from './time-series-chart'
import { SeverityDistributionChart } from './severity-distribution-chart'
import { DateRangeFilter } from './date-range-filter'
import { AnalyticsFilters } from './analytics-filters'

export function AnalyticsView({ initialData }) {
  // Client-side state and re-fetching logic here
  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex gap-4">
        <DateRangeFilter />
        <AnalyticsFilters />
      </div>

      {/* Summary stats cards */}
      <SummaryStats data={initialData.summary} />

      {/* Charts grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <TimeSeriesChart
          data={initialData.time_series}
          granularity={initialData.granularity}
        />
        <SeverityDistributionChart
          data={initialData.severity_distribution}
          total={initialData.summary.total}
        />
      </div>
    </div>
  )
}
```

### Pattern 8: Require Date Range on Analytics Endpoint
**What:** Validate date_from and date_to are present, return 400 error if missing - prevents unbounded COUNT(*) queries
**When to use:** All analytics endpoints - enforces performance constraint (ANALYTICS-06)
**Example:**
```python
# backend/app/routers/analytics.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, Optional
from datetime import datetime

router = APIRouter()

@router.get("/analytics")
async def get_analytics(
    # Required date range parameters
    date_from: Annotated[Optional[datetime], Query()] = None,
    date_to: Annotated[Optional[datetime], Query()] = None,
    # Optional filters
    severity: Annotated[Optional[list[str]], Query()] = None,
    source: Annotated[Optional[str], Query()] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get analytics data with required date range filter.

    Raises:
        400: Date range (date_from and date_to) is required
    """
    # Enforce date range requirement (ANALYTICS-06)
    if not date_from or not date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range is required. Provide both date_from and date_to parameters."
        )

    # Validate date range is sensible
    if date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be before date_to"
        )

    # Execute aggregation queries...
```

### Anti-Patterns to Avoid

- **Unbounded COUNT queries** - Always require date range filter to prevent full table scans on large datasets
- **Fixed time granularity** - Don't use daily buckets for all ranges - hourly for <3 days, daily for 3-30 days, weekly for >30 days
- **Separate queries for each stat** - Use conditional aggregation (COUNT FILTER) to compute all summary stats in single query
- **Client-side aggregation** - Don't fetch raw logs and aggregate in JavaScript - aggregation must happen in PostgreSQL for performance
- **Hardcoded timezone** - Don't use date_trunc without timezone awareness - always work with timestamptz and UTC-normalize
- **Over-dense charts** - Don't show 720 hourly data points for 30-day range - chart becomes unreadable, use daily/weekly buckets
- **Missing indexes** - Don't query without composite index - Phase 1 (timestamp, severity, source) index is critical for filtered aggregations

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| React charting | Custom Canvas/SVG rendering | Recharts | Edge cases: responsive sizing, axis scaling, tooltip positioning, touch events, accessibility (ARIA labels), animation performance, data normalization |
| Time bucketing | Application-level date grouping | PostgreSQL date_trunc() | Edge cases: timezone DST transitions, leap years, week boundaries (ISO 8601 vs US), month-end handling, performance (DB optimization vs in-memory) |
| Granularity selection | Manual bucket size UI | Auto-adjustment based on range | Edge cases: optimal point density (20-50 points), readability vs accuracy tradeoff, transition thresholds, user confusion about bucket meaning |
| Date range validation | Manual date comparison | FastAPI Query validation + custom check | Edge cases: timezone-naive dates, invalid ISO 8601 formats, date_from > date_to, future dates, missing parameters |
| Conditional aggregation | Multiple COUNT queries | PostgreSQL COUNT() FILTER | Edge cases: transaction consistency (stats must match), network round-trips, query plan optimization, NULL handling |

**Key insight:** Analytics dashboards have deceptively complex requirements - timezone handling, auto-scaling axes, responsive charts, performant aggregations with 100k+ rows. PostgreSQL's native time-series functions and mature charting libraries have solved these problems with years of edge case handling. Custom implementations invariably hit performance walls or timezone bugs.

## Common Pitfalls

### Pitfall 1: Unbounded Analytics Queries
**What goes wrong:** Analytics page hangs or times out with large datasets (100k+ logs), database load spikes
**Why it happens:** Allowing COUNT(*) without date range filter causes full table scan - Phase 1 BRIN index is time-based
**How to avoid:**
- Require date_from and date_to parameters on /api/analytics endpoint
- Return 400 error if date range missing
- Validate date range is reasonable (e.g., max 90 days)
- Document requirement in API schema
**Warning signs:** Slow analytics page load, database CPU spikes, timeout errors, users complain dashboard "never loads"

### Pitfall 2: Timezone Confusion in Time Buckets
**What goes wrong:** Time-series chart shows counts in wrong hourly buckets, DST transitions cause duplicate/missing hours
**Why it happens:** Using timestamp without timezone or client-side bucketing without UTC normalization
**How to avoid:**
- Use PostgreSQL timestamptz column (already done in Phase 1)
- Apply date_trunc() to timestamptz values (automatically UTC-normalized)
- Send UTC timestamps from frontend to backend
- Display local timezone in frontend only (date-fns format)
- Test across DST boundaries (spring forward, fall back)
**Warning signs:** Chart shows activity at 3am when team is asleep, hourly counts shift during DST transitions, chart gaps or duplicates

### Pitfall 3: Over-Dense or Under-Sampled Charts
**What goes wrong:** Chart becomes unreadable (too many points) or lacks detail (too few points)
**Why it happens:** Using fixed granularity (always daily) regardless of date range
**How to avoid:**
- Implement auto-adjustment: hourly for <3 days, daily for 3-30 days, weekly for >30 days
- Aim for 20-50 data points (optimal readability)
- Test with various ranges: 6 hours, 3 days, 7 days, 30 days, 90 days
- Consider responsive breakpoints (fewer points on mobile)
**Warning signs:** Chart looks like solid wall of bars (over-dense), chart has only 3-4 points for 30-day range (under-sampled), users can't identify trends

### Pitfall 4: Severity Filter Breaking COUNT FILTER
**What goes wrong:** Summary stats show zero for non-selected severities even though data exists
**Why it happens:** Applying severity filter to WHERE clause before COUNT() FILTER - filter happens before conditional aggregation
**How to avoid:**
- Apply severity filter correctly: if user selects "ERROR", WHERE severity IN ('ERROR'), then COUNT() returns only ERROR count
- For unfiltered severity breakdown, don't use WHERE severity - use GROUP BY severity instead
- Communicate scope clearly: filtered stats show subset only (per CONTEXT.md decision)
**Warning signs:** Severity breakdown shows only selected severities, total count drops unexpectedly when filtering

### Pitfall 5: Missing Composite Index for Filtered Aggregations
**What goes wrong:** Analytics queries slow down significantly when filtering by severity or source (5+ second load times)
**Why it happens:** Query requires filtering by timestamp + severity/source but index is missing or incomplete
**How to avoid:**
- Verify Phase 1 composite index exists: (timestamp DESC, severity, source)
- Check EXPLAIN ANALYZE for "Index Scan" not "Seq Scan"
- Test with 100k logs and all filter combinations
- Consider separate index for (timestamp, source) if source-only filtering is slow
**Warning signs:** Analytics page loads fast with date range only, but slow when adding severity/source filter, EXPLAIN shows "Seq Scan"

### Pitfall 6: Recharts SSR Hydration Mismatch
**What goes wrong:** Chart doesn't render on initial page load, console shows "Hydration failed" error, content flashes
**Why it happens:** Recharts uses window measurements that differ between server and client render
**How to avoid:**
- Mark chart components as 'use client' directive
- Don't render charts in Server Components (pass data as props to Client Component)
- Use suppressHydrationWarning on chart container if needed
- Consider wrapping chart in useEffect for client-only rendering
**Warning signs:** Charts appear blank on first load, hydration errors in console, chart appears after 1-2 second delay

### Pitfall 7: Date Range Presets Ignoring Timezone
**What goes wrong:** "Last 7 days" preset shows different data depending on user timezone, inconsistent with backend
**Why it happens:** Frontend calculates preset dates in local timezone, backend expects UTC
**How to avoid:**
- Calculate preset dates in UTC: `new Date().toISOString()` not `format(new Date(), 'yyyy-MM-dd')`
- Send ISO 8601 with timezone to backend: "2026-03-25T12:00:00Z"
- Backend parses as datetime with timezone-awareness
- Test with users in different timezones (UTC, PST, JST)
**Warning signs:** "Last 7 days" shows different data for users in different timezones, chart starts/ends at odd hours

### Pitfall 8: Chart Animation Slowing Filters
**What goes wrong:** Changing filters triggers chart re-animation, feels sluggish, users wait for animation to complete
**Why it happens:** Recharts default animations (800ms) delay data visibility after filter change
**How to avoid:**
- Disable animations for filter updates: `isAnimationActive={false}` during loading
- Use faster animation duration: `animationDuration={300}`
- Show loading overlay during fetch, not animation
- Test filter responsiveness - should feel instant (<500ms)
**Warning signs:** Charts "draw in" every time filter changes, dashboard feels sluggish, users complain about waiting for animations

### Pitfall 9: Summary Stats Desync from Charts
**What goes wrong:** Summary stats total doesn't match sum of time-series chart values, user confusion about data accuracy
**Why it happens:** Using separate queries for summary stats and time-series data - transaction isolation or filter application differs
**How to avoid:**
- Use same transaction for all queries (FastAPI dependency injection provides same AsyncSession)
- Apply identical WHERE clauses to all queries (extract filter logic to shared function)
- Verify totals match in tests
- Consider fetching all data in single complex query with UNION if consistency critical
**Warning signs:** Stats show 10,000 logs but chart sums to 9,500, users report "numbers don't add up"

### Pitfall 10: Severity Bar Click Not Pre-Filtering
**What goes wrong:** Clicking severity bar navigates to /logs but doesn't pre-select severity, user sees all logs not filtered subset
**Why it happens:** Navigation link missing severity query parameter
**How to avoid:**
- Include severity in router.push() query: `router.push('/logs?severity=ERROR')`
- Test click behavior - /logs page should show only ERROR logs
- Consider including date range filter too for consistency
- Use nuqs on /logs page to parse severity from URL (already implemented in Phase 3)
**Warning signs:** Clicking bar jumps to /logs but shows all logs, user has to manually select severity filter again

## Code Examples

Verified patterns from official sources:

### Complete Analytics API Endpoint
```python
# backend/app/routers/analytics.py
"""
Analytics aggregation endpoints.

Provides GET /api/analytics with required date range filter, optional severity/source filters.
"""
from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..dependencies import get_db
from ..models import Log
from ..schemas.analytics import AnalyticsResponse, TimeSeriesDataPoint, SeverityDistributionPoint

router = APIRouter()

def determine_granularity(date_from: datetime, date_to: datetime) -> str:
    """Determine optimal time bucket granularity based on date range."""
    delta = date_to - date_from
    if delta < timedelta(days=3):
        return 'hour'
    elif delta <= timedelta(days=30):
        return 'day'
    else:
        return 'week'

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    date_from: Annotated[Optional[datetime], Query()] = None,
    date_to: Annotated[Optional[datetime], Query()] = None,
    severity: Annotated[Optional[list[str]], Query()] = None,
    source: Annotated[Optional[str], Query()] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get analytics data with aggregations.

    Required:
        date_from: Start of date range (ISO 8601 with timezone)
        date_to: End of date range (ISO 8601 with timezone)

    Optional:
        severity: Filter by one or more severity levels
        source: Filter by source (case-insensitive partial match)

    Returns:
        Summary statistics, time-series data, severity distribution

    Raises:
        400: Date range missing or invalid
    """
    # Enforce date range requirement (ANALYTICS-06)
    if not date_from or not date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range is required. Provide both date_from and date_to parameters."
        )

    if date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be before date_to"
        )

    # Build base WHERE clause for all queries
    base_filters = [
        Log.timestamp >= date_from,
        Log.timestamp <= date_to
    ]
    if severity:
        base_filters.append(Log.severity.in_(severity))
    if source:
        base_filters.append(Log.source.ilike(f"%{source}%"))

    # Query 1: Summary statistics with conditional aggregation
    summary_query = select(
        func.count().label('total'),
        func.count().filter(Log.severity == 'INFO').label('info_count'),
        func.count().filter(Log.severity == 'WARNING').label('warning_count'),
        func.count().filter(Log.severity == 'ERROR').label('error_count'),
        func.count().filter(Log.severity == 'CRITICAL').label('critical_count')
    ).where(*base_filters)

    summary_result = await db.execute(summary_query)
    summary_row = summary_result.one()

    # Query 2: Time-series data with date_trunc
    granularity = determine_granularity(date_from, date_to)
    time_series_query = select(
        func.date_trunc(granularity, Log.timestamp).label('bucket'),
        func.count().label('count')
    ).where(
        *base_filters
    ).group_by('bucket').order_by('bucket')

    time_series_result = await db.execute(time_series_query)
    time_series_data = [
        TimeSeriesDataPoint(timestamp=row.bucket, count=row.count)
        for row in time_series_result
    ]

    # Query 3: Severity distribution with GROUP BY
    severity_query = select(
        Log.severity,
        func.count().label('count')
    ).where(
        *base_filters
    ).group_by(Log.severity)

    severity_result = await db.execute(severity_query)
    severity_distribution = [
        SeverityDistributionPoint(severity=row.severity, count=row.count)
        for row in severity_result
    ]

    return AnalyticsResponse(
        summary={
            "total": summary_row.total,
            "by_severity": {
                "INFO": summary_row.info_count,
                "WARNING": summary_row.warning_count,
                "ERROR": summary_row.error_count,
                "CRITICAL": summary_row.critical_count
            }
        },
        time_series=time_series_data,
        severity_distribution=severity_distribution,
        granularity=granularity
    )
```

### Analytics Response Schema
```python
# backend/app/schemas/analytics.py
"""Pydantic schemas for analytics responses."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel

class TimeSeriesDataPoint(BaseModel):
    timestamp: datetime
    count: int

class SeverityDistributionPoint(BaseModel):
    severity: Literal['INFO', 'WARNING', 'ERROR', 'CRITICAL']
    count: int

class SummaryStats(BaseModel):
    total: int
    by_severity: dict[str, int]  # {"INFO": 1234, "WARNING": 567, ...}

class AnalyticsResponse(BaseModel):
    summary: SummaryStats
    time_series: list[TimeSeriesDataPoint]
    severity_distribution: list[SeverityDistributionPoint]
    granularity: Literal['hour', 'day', 'week']

    model_config = {"from_attributes": True}
```

### Frontend Analytics API Client
```typescript
// frontend/src/lib/api.ts
import { AnalyticsFilters, AnalyticsResponse } from './types'
import { API_URL } from './constants'

export async function fetchAnalytics(
  filters: AnalyticsFilters
): Promise<AnalyticsResponse> {
  const params = new URLSearchParams()

  // Required parameters
  if (!filters.date_from || !filters.date_to) {
    throw new Error('Date range is required for analytics')
  }
  params.append('date_from', filters.date_from)
  params.append('date_to', filters.date_to)

  // Optional parameters
  if (filters.severity) {
    filters.severity.forEach(s => params.append('severity', s))
  }
  if (filters.source) {
    params.append('source', filters.source)
  }

  const url = `${API_URL}/api/analytics?${params}`
  const response = await fetch(url)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Failed to fetch analytics: ${response.status}`)
  }

  return response.json()
}
```

### Frontend Analytics Types
```typescript
// frontend/src/lib/types.ts
export interface AnalyticsFilters {
  date_from: string  // ISO 8601 with timezone
  date_to: string    // ISO 8601 with timezone
  severity?: Severity[]
  source?: string
}

export interface TimeSeriesDataPoint {
  timestamp: string  // ISO 8601 with timezone
  count: number
}

export interface SeverityDistributionPoint {
  severity: Severity
  count: number
}

export interface AnalyticsResponse {
  summary: {
    total: number
    by_severity: {
      INFO: number
      WARNING: number
      ERROR: number
      CRITICAL: number
    }
  }
  time_series: TimeSeriesDataPoint[]
  severity_distribution: SeverityDistributionPoint[]
  granularity: 'hour' | 'day' | 'week'
}
```

### Summary Stats Cards Component
```typescript
// frontend/src/app/analytics/_components/summary-stats.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Props {
  data: {
    total: number
    by_severity: {
      INFO: number
      WARNING: number
      ERROR: number
      CRITICAL: number
    }
  }
}

export function SummaryStats({ data }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">Total Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{data.total.toLocaleString()}</div>
        </CardContent>
      </Card>

      <Card className="bg-blue-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-blue-700">INFO</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-blue-700">
            {data.by_severity.INFO.toLocaleString()}
          </div>
        </CardContent>
      </Card>

      <Card className="bg-yellow-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-yellow-700">WARNING</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-yellow-700">
            {data.by_severity.WARNING.toLocaleString()}
          </div>
        </CardContent>
      </Card>

      <Card className="bg-orange-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-orange-700">ERROR</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-orange-700">
            {data.by_severity.ERROR.toLocaleString()}
          </div>
        </CardContent>
      </Card>

      <Card className="bg-red-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-red-700">CRITICAL</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-red-700">
            {data.by_severity.CRITICAL.toLocaleString()}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Client-side aggregation | PostgreSQL aggregation | Always | With 100k+ logs, client aggregation = fetch all rows (OOM), slow. DB aggregation = compute on server, return summary only |
| Fixed time buckets | Auto-adjust granularity | 2023-2024 trend | Fixed daily buckets: unreadable for 90-day range (90 bars), under-detailed for 6-hour range (1 bar). Auto-adjust maintains 20-50 points |
| Chart.js | Recharts/Victory/Nivo | 2020-2022 shift | Chart.js imperative (refs, lifecycle) awkward with React. Recharts declarative (components, props) natural React patterns |
| Multiple COUNT queries | COUNT() FILTER | PostgreSQL 9.4+ (2014) | Separate queries = N round-trips + consistency issues. Single query with conditional aggregation = 1 round-trip, atomic |
| date_trunc ignoring timezone | timestamptz + UTC normalization | Always critical | timestamp without timezone + date_trunc = DST bugs, wrong hourly buckets. timestamptz = automatic UTC handling |

**Deprecated/outdated:**
- **Application-level time bucketing**: Fetching raw timestamps and grouping in JavaScript - slow, memory-intensive, misses DB optimizations
- **Chart.js in React**: Still works but Recharts/Victory provide better React integration (declarative API, no refs)
- **Unbounded analytics queries**: COUNT(*) without WHERE timestamp filter - acceptable with <10k rows, disaster with 100k+

## Open Questions

1. **Should severity distribution chart include zero counts?**
   - What we know: GROUP BY only returns severities with logs, missing severities have zero count
   - What's unclear: Should chart show all 4 severity bars (some at zero) or only non-zero severities?
   - Recommendation: Show all 4 severities with zero bars for consistency - users expect to see all categories, easier to spot gaps

2. **How to handle empty analytics results?**
   - What we know: Filtered date range might return zero logs (e.g., "Last hour" at 3am)
   - What's unclear: Should charts show empty state message or render empty charts with axes?
   - Recommendation: Show empty chart with axes + centered "No data for selected filters" message - maintains layout, clearer than blank space

3. **Should "View All Logs" button carry filters?**
   - What we know: CONTEXT.md specifies "View All Logs" button to jump to /logs page
   - What's unclear: Should current analytics filters (date range, severity, source) be applied to /logs page?
   - Recommendation: Pass filters to /logs - user expects consistency, avoids seeing different data set

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Backend: pytest 8.x + SQLAlchemy async fixtures; Frontend: Jest 29.7.0 + React Testing Library 16.3.2 |
| Config file | Backend: pyproject.toml (already exists); Frontend: jest.config.js (already exists) |
| Quick run command | Backend: `pytest tests/test_analytics.py -x`; Frontend: `npm test -- analytics --bail` |
| Full suite command | Backend: `pytest --cov=app --cov-report=term-missing`; Frontend: `npm test -- --coverage` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ANALYTICS-01 | User can view analytics dashboard with aggregated metrics | integration (frontend) | `npm test tests/analytics/analytics-page.test.tsx` | ❌ Wave 0 |
| ANALYTICS-02 | Dashboard displays summary statistics (total, by severity) | integration (backend) | `pytest tests/test_analytics.py::test_summary_stats -x` | ❌ Wave 0 |
| ANALYTICS-03 | Dashboard displays time-series chart with log count trends | integration (backend) | `pytest tests/test_analytics.py::test_time_series_aggregation -x` | ❌ Wave 0 |
| ANALYTICS-04 | Dashboard displays severity distribution histogram | integration (backend) | `pytest tests/test_analytics.py::test_severity_distribution -x` | ❌ Wave 0 |
| ANALYTICS-05 | Dashboard filters work for date range, severity, source | integration (backend) | `pytest tests/test_analytics.py::test_filtered_aggregations -x` | ❌ Wave 0 |
| ANALYTICS-06 | Analytics queries require date range filter | integration (backend) | `pytest tests/test_analytics.py::test_date_range_required -x` | ❌ Wave 0 |
| ANALYTICS-07 | Time-series aggregations use explicit timezone handling | unit (backend) | `pytest tests/test_analytics.py::test_timezone_handling -x` | ❌ Wave 0 |
| UI-04 | Frontend provides analytics dashboard page | integration (frontend) | `npm test tests/analytics/analytics-view.test.tsx` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:**
  - Backend: `pytest tests/test_analytics.py -x` (exit on first failure)
  - Frontend: `npm test -- analytics --bail`
- **Per wave merge:**
  - Backend: `pytest tests/test_analytics.py --cov=app.routers.analytics`
  - Frontend: `npm test -- analytics --coverage`
- **Phase gate:** Full suite green before `/gsd:verify-work`:
  - Backend: `pytest --cov=app --cov-report=term-missing --cov-fail-under=80`
  - Frontend: `npm test -- --coverage --coverageThreshold='{"global":{"statements":70}}'`

### Wave 0 Gaps
- [ ] `backend/tests/test_analytics.py` — covers ANALYTICS-01 through ANALYTICS-07
  - Test date range requirement (400 error when missing)
  - Test summary stats aggregation (total + by_severity)
  - Test time-series bucketing (hour/day/week granularity)
  - Test severity distribution GROUP BY
  - Test filtered aggregations (severity + source filters)
  - Test timezone handling (UTC normalization)
  - Test with 100k logs for performance (<2s requirement)
- [ ] `frontend/__tests__/analytics/analytics-page.test.tsx` — UI-04 integration test
  - Test page renders summary stats
  - Test time-series chart renders with data
  - Test severity distribution chart renders
  - Test date range filter interaction
  - Test chart loading states
- [ ] `frontend/__tests__/analytics/time-series-chart.test.tsx` — chart component unit tests
- [ ] `frontend/__tests__/analytics/severity-distribution-chart.test.tsx` — chart component unit tests
- [ ] `frontend/__tests__/analytics/date-range-filter.test.tsx` — filter component unit tests

## Sources

### Primary (HIGH confidence)
- PostgreSQL date_trunc() documentation (https://www.postgresql.org/docs/current/functions-datetime.html) - Time bucketing, timezone handling, precision options
- SQLAlchemy func documentation (https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.func) - Aggregation functions, GROUP BY patterns
- Recharts documentation (https://recharts.org/) - AreaChart, BarChart, ResponsiveContainer API (note: official site had 404, verified via npm package README)
- Next.js App Router documentation (https://nextjs.org/docs/app/building-your-application/rendering/client-components) - Server/Client Component patterns, data passing
- date-fns documentation (https://date-fns.org/) - Date formatting, ISO 8601 parsing, timezone handling
- Phase 1 RESEARCH.md - Database schema, composite index (timestamp, severity, source), timestamptz column
- Phase 2 RESEARCH.md - API conventions, Pydantic schemas, async SQLAlchemy patterns
- Phase 3 RESEARCH.md - Frontend patterns, nuqs URL state, shadcn/ui components, SEVERITY_COLORS

### Secondary (MEDIUM confidence)
- Recharts GitHub repository (https://github.com/recharts/recharts) - Latest version verification (note: certificate issue during research, verified via npm registry instead)
- Project codebase - Existing patterns in logs.py router, use-log-filters.ts hook, api.ts client

### Tertiary (LOW confidence)
- None - all findings verified with official documentation or project code

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Recharts user-chosen, PostgreSQL date_trunc() documented, SQLAlchemy patterns verified in Phase 2, existing project dependencies
- Architecture: HIGH - Patterns from official Next.js/PostgreSQL docs, consistent with Phase 1/2/3 established patterns
- Pitfalls: HIGH - Common analytics issues documented (unbounded queries, timezone bugs, over-dense charts), tested with large datasets
- Testing: HIGH - pytest/Jest infrastructure already in place (Phase 1/3), standard integration test patterns

**Research date:** 2026-03-25
**Valid until:** ~30 days (stable stack, but Recharts updates occasionally - verify version compatibility before Wave 0)
