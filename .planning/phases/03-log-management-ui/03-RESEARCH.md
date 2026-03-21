# Phase 3: Log Management UI - Research

**Researched:** 2026-03-21
**Domain:** Next.js 15 + React 19 frontend development
**Confidence:** HIGH

## Summary

Phase 3 requires building a responsive log management interface using Next.js 15 App Router with React 19. The frontend consumes the REST API completed in Phase 2, implementing log list with infinite scroll, filtering/searching with URL state persistence, and modal-based log detail views.

Key architectural decisions: Next.js App Router (not Pages Router) with Server Components for initial data fetch and Client Components for interactive features (filters, search, modal). shadcn/ui provides accessible, customizable components. TanStack Virtual handles performant infinite scroll. nuqs manages URL state for shareable filtered views. Tailwind CSS for styling.

The stack follows modern React patterns: server-first rendering, progressive enhancement, minimal client JavaScript, and type-safe end-to-end development with TypeScript mirroring backend Pydantic schemas.

**Primary recommendation:** Use Next.js App Router with shadcn/ui + TanStack Virtual + nuqs for a production-ready, accessible, performant log management UI.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Page Structure & Navigation:**
- Routing: Separate routes with persistent sidebar navigation
- Sidebar items: "Logs" and "Create Log" (Dashboard added in Phase 5)
- Log detail: Modal overlay on list page (not separate route) - URL can update via query param
- Page titles: Simple H1 only ("Logs", "Create Log") - no breadcrumbs
- Layout consistency: Sidebar persists across all pages

**Log List Display:**
- Table style: Borderless table with modern clean aesthetic, subtle row hover
- Columns: Severity (as colored badge) + Message (primary content) + Timestamp (right-aligned)
- Severity badges: Color-coded backgrounds only (INFO=blue, WARNING=yellow, ERROR=red, CRITICAL=dark red) - no icons
- Pagination: Infinite scroll with virtual scrolling (auto-load more on scroll, virtualization for performance)
- Row interaction: Hover highlights row background, click anywhere on row opens detail modal
- Sorting: Clickable column headers with sort direction icons (▲/▼) - API supports timestamp/severity/source sorting
- Empty state: "No logs yet. Create your first log!" with prominent Create Log button

**Filter & Search UI:**
- Filter position: Left sidebar panel next to table (vertical layout)
- Search input: Debounced real-time search (300-500ms debounce) - search message content as you type
- Date range: Two separate date inputs (Start Date, End Date) - simple HTML date inputs or basic date picker
- Severity filter: Multi-select dropdown allowing multiple selections (INFO, WARNING, ERROR, CRITICAL)
- Source filter: Dropdown or text input (case-insensitive matching per Phase 2 API)
- Active filter visibility: Filter chips above table showing active filters with X to remove ("Severity: ERROR [x]", "Source: api-service [x]")
- URL state: Filter state preserved in URL search params (?search=error&severity=ERROR&date_from=2024-01-01) for shareable links
- Clear filters: "Reset Filters" button at bottom of filter sidebar panel

**Loading & Error States:**
- Loading indicator: Skeleton rows in table (gray shimmer/pulse animation) - maintains layout, feels fast
- Error display: Toast notification (top-right corner) that auto-dismisses - non-blocking for transient errors
- Optimistic UI: Form submissions show immediately in list, rollback on API error
- Retry logic: Automatic retry (1-2 attempts) for failed requests before showing error to user

### Claude's Discretion

- Exact component library choice (shadcn/ui, Headless UI, or custom)
- Skeleton animation style (pulse, shimmer, wave)
- Toast auto-dismiss timing
- Exact debounce delay (300-500ms range)
- Modal transition animations
- Responsive breakpoint adjustments
- Infinite scroll trigger point (how far from bottom)
- Virtual scroll library (react-window, react-virtual, or custom)

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| UI-01 | Frontend provides log list page with search, filter, sort, pagination controls | Next.js App Router routing + TanStack Virtual infinite scroll + nuqs URL state + shadcn/ui components |
| UI-02 | Frontend provides log detail page | Next.js intercepting routes pattern for modal overlay + shadcn/ui Dialog component |
| UI-03 | Frontend provides log creation page/form | Next.js App Router routing + react-hook-form + zod validation + shadcn/ui form components |
| UI-05 | Frontend uses React Server Components for data fetching | Next.js App Router default behavior - Server Components fetch initial data, pass to Client Components |
| UI-06 | Frontend uses Client Components only for interactive features | 'use client' directive for filters, search, modal, form - keeps most UI as Server Components |
| UI-07 | Frontend displays loading states during data fetch | Skeleton components (shadcn/ui Skeleton) + React Suspense boundaries |
| UI-08 | Frontend displays meaningful error messages | Sonner toast notifications for transient errors + error boundaries for fatal errors |
| UI-09 | Frontend is responsive across desktop and tablet screen sizes | Tailwind CSS responsive utilities + mobile-first breakpoints (sm:, md:, lg:, xl:, 2xl:) |
| FILTER-01 | User can search logs by message content | Debounced search input (300-500ms) + nuqs for URL state + API ?search= parameter |
| FILTER-02 | User can filter logs by date range (start date, end date) | Date inputs (HTML date or shadcn/ui Calendar) + nuqs for URL state + API ?date_from= & ?date_to= parameters |
| FILTER-03 | User can filter logs by severity level | Multi-select dropdown (shadcn/ui Select) + nuqs for URL state + API ?severity= repeated parameters |
| FILTER-04 | User can filter logs by source | Dropdown or text input (shadcn/ui Select or Input) + nuqs for URL state + API ?source= parameter |
| FILTER-05 | User can apply multiple filters simultaneously | nuqs useQueryStates manages multiple URL params + API accepts combined filters |
| FILTER-06 | User can sort logs by any column (timestamp, severity, source) | Clickable column headers + nuqs for URL state + API ?sort= & ?order= parameters |
| FILTER-07 | Filter state persists when navigating between pages | nuqs syncs state with URL search params - browser back/forward/refresh preserves filters |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| next | 15.x (latest stable) | React framework with App Router | Official Next.js 15 released with React 19 support, App Router is production-ready and recommended over Pages Router |
| react | 19.x (latest stable) | UI library with Server Components | React 19 released December 2024, includes stable Server Components and new hooks |
| typescript | 5.5+ | Type safety | Required by project constraints, Zod requires 5.5+ with strict mode |
| tailwindcss | 3.x (latest) | Utility-first CSS | Official Next.js recommendation, zero-runtime styling, excellent DX |
| shadcn/ui | CLI-based | Accessible component primitives | Industry standard for customizable, accessible React components - code ownership model |
| @tanstack/react-virtual | 3.x (latest) | Virtual scrolling | TanStack Virtual is the modern replacement for react-window, smaller (10-15kb), actively maintained |
| nuqs | 2.x (latest) | URL state management | Type-safe, framework-agnostic, 6kb, adopted by Vercel/Supabase/shadcn - eliminates manual URLSearchParams parsing |
| react-hook-form | 7.x (latest) | Form state management | Performance-focused (minimal re-renders), won 2020 GitNation award, industry standard |
| zod | 3.x (latest) | Schema validation | TypeScript-first, 2kb gzipped, zero dependencies, integrates with react-hook-form via @hookform/resolvers |
| sonner | 1.x (latest) | Toast notifications | Opinionated, accessible toast library by shadcn/ui ecosystem, simple API |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @radix-ui/react-* | Various | Headless UI primitives | Automatically installed by shadcn/ui CLI - provides accessible foundation (Dialog, Select, etc.) |
| clsx / tailwind-merge | Latest | Conditional class names | For dynamic Tailwind classes, handle conflicts - standard pattern in Tailwind projects |
| @hookform/resolvers | 3.x | Form validation adapters | Bridges react-hook-form and zod - required for schema validation |
| date-fns | 3.x | Date formatting/parsing | For date manipulation, ISO 8601 parsing, locale-aware formatting - lighter than moment.js |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| shadcn/ui | Headless UI (Tailwind Labs) | Less customizable (wrapper-based), but simpler if minimal customization needed |
| shadcn/ui | Radix UI directly | More control but no defaults - need to style everything from scratch |
| TanStack Virtual | react-window | Older library (35kb vs 10kb), less flexible API, but battle-tested |
| nuqs | Manual URLSearchParams | More control but boilerplate-heavy, no type safety, error-prone |
| react-hook-form | Formik | More popular historically but slower, more re-renders, larger bundle |
| Tailwind CSS | CSS Modules | Better scoping, but verbose, no utility-first benefits, harder to maintain |

**Installation:**
```bash
# Initialize Next.js 15 with TypeScript + Tailwind
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir --import-alias "@/*"

# Initialize shadcn/ui
npx shadcn@latest init -t next

# Add shadcn/ui components (example - add as needed)
npx shadcn@latest add button dialog select input skeleton table toast

# Install additional dependencies
npm install @tanstack/react-virtual nuqs react-hook-form zod @hookform/resolvers sonner date-fns
```

## Architecture Patterns

### Recommended Project Structure
```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx           # Root layout with sidebar navigation
│   │   ├── page.tsx             # Home page (redirect to /logs)
│   │   ├── logs/                # Log list page
│   │   │   ├── page.tsx         # Server Component - initial data fetch
│   │   │   ├── _components/     # Client Components for interactivity
│   │   │   │   ├── log-list.tsx       # Main list with infinite scroll + virtual
│   │   │   │   ├── log-filters.tsx    # Filter sidebar with nuqs
│   │   │   │   ├── log-table.tsx      # Table with sorting + row click
│   │   │   │   ├── log-detail-modal.tsx # Modal overlay
│   │   │   │   └── skeleton-rows.tsx  # Loading state
│   │   │   └── @modal/          # Parallel route for modal (optional pattern)
│   │   └── create/              # Log creation page
│   │       ├── page.tsx         # Server Component wrapper
│   │       └── _components/
│   │           └── create-form.tsx # Client Component with react-hook-form
│   ├── components/              # Reusable components
│   │   ├── ui/                  # shadcn/ui components (generated by CLI)
│   │   ├── nav/
│   │   │   └── sidebar.tsx      # Persistent sidebar navigation
│   │   └── shared/
│   │       ├── error-toast.tsx  # Toast notification wrapper
│   │       └── severity-badge.tsx # Colored severity indicator
│   ├── lib/                     # Utilities
│   │   ├── api.ts               # API client functions (fetch wrappers)
│   │   ├── types.ts             # TypeScript types mirroring backend schemas
│   │   ├── utils.ts             # Shared utilities (cn, formatDate, etc.)
│   │   └── constants.ts         # Constants (API_URL, severity colors, etc.)
│   └── hooks/                   # Custom React hooks
│       ├── use-logs.ts          # Data fetching hook for log list
│       ├── use-debounce.ts      # Debounce hook for search input
│       └── use-infinite-scroll.ts # Infinite scroll logic with TanStack Virtual
├── public/                      # Static assets
├── next.config.js               # Next.js configuration
├── tailwind.config.ts           # Tailwind configuration
├── tsconfig.json                # TypeScript configuration
└── package.json
```

### Pattern 1: Server Component → Client Islands
**What:** Page-level Server Components fetch initial data and pass to Client Component islands for interactivity
**When to use:** Default pattern for all pages - maximize server rendering, minimize client JavaScript
**Example:**
```typescript
// app/logs/page.tsx (Server Component)
import { LogList } from './_components/log-list'

export default async function LogsPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  // Fetch initial data on server
  const initialData = await fetch(`${process.env.API_URL}/api/logs?limit=50`).then(r => r.json())

  return (
    <div>
      <h1>Logs</h1>
      {/* Pass initial data to Client Component */}
      <LogList initialData={initialData} />
    </div>
  )
}

// app/logs/_components/log-list.tsx (Client Component)
'use client'

import { useInfiniteScroll } from '@/hooks/use-infinite-scroll'

export function LogList({ initialData }) {
  const { data, loadMore, isLoading } = useInfiniteScroll(initialData)
  // Client-side interactivity here
  return <div>{/* ... */}</div>
}
```

### Pattern 2: URL State Management with nuqs
**What:** Sync filter/search state with URL search params for shareable links
**When to use:** All stateful filters, search inputs, and sorting - enables shareable URLs and browser back/forward
**Example:**
```typescript
// app/logs/_components/log-filters.tsx
'use client'

import { useQueryStates, parseAsString, parseAsArrayOf } from 'nuqs'

export function LogFilters() {
  const [filters, setFilters] = useQueryStates({
    search: parseAsString.withDefault(''),
    severity: parseAsArrayOf(parseAsString).withDefault([]),
    source: parseAsString.withDefault(''),
    date_from: parseAsString.withDefault(''),
    date_to: parseAsString.withDefault(''),
    sort: parseAsString.withDefault('timestamp'),
    order: parseAsString.withDefault('desc'),
  })

  // Update URL automatically on filter change
  const handleSearchChange = (value: string) => {
    setFilters({ search: value })
  }

  // URL updates: /logs?search=error&severity=ERROR&severity=WARNING
  return <div>{/* Filter UI */}</div>
}
```

### Pattern 3: Infinite Scroll + Virtual Scrolling
**What:** Load more data as user scrolls (infinite scroll) + render only visible rows (virtual scrolling)
**When to use:** Log list with 10k-100k potential rows - prevents memory issues and maintains 60fps
**Example:**
```typescript
// app/logs/_components/log-table.tsx
'use client'

import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef } from 'react'

export function LogTable({ logs, onLoadMore, hasMore }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const rowVirtualizer = useVirtualizer({
    count: logs.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 56, // Row height in pixels
    overscan: 5, // Render 5 extra rows above/below viewport
  })

  const items = rowVirtualizer.getVirtualItems()
  const lastItem = items[items.length - 1]

  // Trigger load more when scrolling near bottom
  useEffect(() => {
    if (lastItem && lastItem.index >= logs.length - 10 && hasMore) {
      onLoadMore()
    }
  }, [lastItem, hasMore, logs.length, onLoadMore])

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, position: 'relative' }}>
        {items.map((virtualRow) => (
          <div
            key={virtualRow.index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            {/* Row content */}
          </div>
        ))}
      </div>
    </div>
  )
}
```

### Pattern 4: Modal with URL State (Intercepting Routes)
**What:** Show modal overlay on current page while updating URL (enables direct linking and back button)
**When to use:** Log detail modal - preserves filter context, allows sharing specific log URL
**Example:**
```typescript
// Option A: Simple approach with query param (recommended for this phase)
// app/logs/_components/log-table.tsx
'use client'

import { useQueryState } from 'nuqs'
import { LogDetailModal } from './log-detail-modal'

export function LogTable({ logs }) {
  const [selectedLogId, setSelectedLogId] = useQueryState('log')

  return (
    <>
      <table>
        {logs.map((log) => (
          <tr key={log.id} onClick={() => setSelectedLogId(log.id.toString())}>
            {/* Row content */}
          </tr>
        ))}
      </table>

      {/* Modal opens when ?log=123 is in URL */}
      {selectedLogId && (
        <LogDetailModal
          logId={selectedLogId}
          onClose={() => setSelectedLogId(null)}
        />
      )}
    </>
  )
}

// Option B: Advanced pattern with intercepting routes (more complex, optional)
// app/logs/@modal/(.)log/[id]/page.tsx
// https://nextjs.org/docs/app/building-your-application/routing/parallel-routes
```

### Pattern 5: Debounced Search with Custom Hook
**What:** Delay API calls until user stops typing (300-500ms) to reduce unnecessary requests
**When to use:** Search inputs, autocomplete, any real-time filtering
**Example:**
```typescript
// hooks/use-debounce.ts
import { useState, useEffect } from 'react'

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => clearTimeout(handler)
  }, [value, delay])

  return debouncedValue
}

// app/logs/_components/search-input.tsx
'use client'

import { useQueryState } from 'nuqs'
import { useDebounce } from '@/hooks/use-debounce'
import { useState } from 'react'

export function SearchInput() {
  const [search, setSearch] = useQueryState('search', { defaultValue: '' })
  const [localValue, setLocalValue] = useState(search)
  const debouncedSearch = useDebounce(localValue, 400) // 400ms delay

  // Update URL only after debounce
  useEffect(() => {
    setSearch(debouncedSearch)
  }, [debouncedSearch, setSearch])

  return (
    <input
      type="text"
      value={localValue}
      onChange={(e) => setLocalValue(e.target.value)}
      placeholder="Search logs..."
    />
  )
}
```

### Pattern 6: Form Validation with react-hook-form + zod
**What:** Type-safe form validation with schema definition, minimal re-renders
**When to use:** Log creation form, any form with validation requirements
**Example:**
```typescript
// lib/types.ts - Mirror backend Pydantic schemas
import { z } from 'zod'

export const logCreateSchema = z.object({
  timestamp: z.string().datetime({ message: 'Must be ISO 8601 format with timezone' }),
  message: z.string().min(1, 'Message is required'),
  severity: z.enum(['INFO', 'WARNING', 'ERROR', 'CRITICAL'], {
    errorMap: () => ({ message: 'Must be INFO, WARNING, ERROR, or CRITICAL' }),
  }),
  source: z.string().min(1, 'Source is required').max(100, 'Source must be ≤100 characters'),
})

export type LogCreate = z.infer<typeof logCreateSchema>

// app/create/_components/create-form.tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { logCreateSchema, type LogCreate } from '@/lib/types'

export function CreateForm() {
  const form = useForm<LogCreate>({
    resolver: zodResolver(logCreateSchema),
    defaultValues: {
      timestamp: new Date().toISOString(),
      message: '',
      severity: 'INFO',
      source: '',
    },
  })

  const onSubmit = async (data: LogCreate) => {
    // API call with validated data
    const response = await fetch('/api/logs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    // Handle response
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  )
}
```

### Pattern 7: TypeScript Types Mirroring Backend
**What:** Define frontend types matching backend Pydantic schemas for end-to-end type safety
**When to use:** All API interactions - ensures frontend and backend stay in sync
**Example:**
```typescript
// lib/types.ts
// Mirror backend/app/schemas/logs.py

export interface LogResponse {
  id: number
  timestamp: string // ISO 8601 with timezone
  message: string
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
  source: string
}

export interface LogListResponse {
  data: LogResponse[]
  next_cursor: string | null
  has_more: boolean
}

export interface LogCreate {
  timestamp: string // ISO 8601 with timezone
  message: string
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
  source: string
}

// lib/api.ts
export async function fetchLogs(params: {
  cursor?: string
  limit?: number
  search?: string
  severity?: string[]
  source?: string
  date_from?: string
  date_to?: string
  sort?: 'timestamp' | 'severity' | 'source'
  order?: 'asc' | 'desc'
}): Promise<LogListResponse> {
  const queryParams = new URLSearchParams()
  if (params.cursor) queryParams.append('cursor', params.cursor)
  if (params.limit) queryParams.append('limit', params.limit.toString())
  if (params.search) queryParams.append('search', params.search)
  if (params.severity) params.severity.forEach(s => queryParams.append('severity', s))
  if (params.source) queryParams.append('source', params.source)
  if (params.date_from) queryParams.append('date_from', params.date_from)
  if (params.date_to) queryParams.append('date_to', params.date_to)
  if (params.sort) queryParams.append('sort', params.sort)
  if (params.order) queryParams.append('order', params.order)

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/logs?${queryParams}`)
  if (!response.ok) throw new Error('Failed to fetch logs')
  return response.json()
}
```

### Anti-Patterns to Avoid

- **Using useState for URL-synced state** - Use nuqs instead to avoid manual URLSearchParams parsing and keep URL in sync
- **Fetching in Client Components without Server Components** - Always fetch initial data in Server Components, use Client Components for subsequent fetches
- **Using 'use client' at root layout** - Only mark interactive components as client, keep layouts/pages as Server Components when possible
- **Uncontrolled infinite scroll** - Without virtual scrolling, rendering 10k+ rows causes memory issues and performance degradation
- **Missing Suspense boundaries** - useSearchParams requires Suspense boundary or causes entire route to client-render
- **Global error handlers without boundaries** - Use error.tsx files and Error Boundaries for graceful error handling
- **Importing Server Components in Client Components** - Cannot import Server Components into 'use client' files (but can pass as children/props)
- **Hydration mismatches** - Server and client must render identical initial HTML (avoid Date.now(), window checks in render)

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Virtual scrolling | Custom scroll detection + manual DOM updates | TanStack Virtual | Edge cases: variable row heights, scroll restoration, resize handling, accessibility (focus management), performance optimization (overscan tuning) |
| URL state sync | Manual URLSearchParams parsing/serialization | nuqs | Edge cases: array parameters, nested objects, type coercion, history management, SSR/CSR sync, TypeScript safety |
| Form validation | Custom validation logic | react-hook-form + zod | Edge cases: field dependencies, async validation, error message management, touched/dirty state, accessibility (ARIA attributes) |
| Toast notifications | Custom toast component | Sonner | Edge cases: stacking, positioning, auto-dismiss, swipe-to-dismiss, accessibility (ARIA live regions), animations |
| Accessible components | Custom modals/dropdowns/selects | shadcn/ui (Radix UI) | Edge cases: keyboard navigation, focus trapping, screen reader announcements, ARIA attributes, escape/outside click handling |
| Debounce utility | Custom setTimeout wrapper | use-debounce hook | Edge cases: cleanup on unmount, multiple simultaneous debounces, TypeScript generics, leading/trailing edge options |
| Date formatting | String manipulation | date-fns | Edge cases: timezone handling, locale support, relative time (e.g., "2 hours ago"), parsing ISO 8601 variants |

**Key insight:** Frontend UI has matured to the point where building accessible, performant, cross-browser compatible components from scratch is rarely justified. The ecosystem provides battle-tested solutions for nearly every common need. Custom implementations invariably miss edge cases that take years to discover and fix.

## Common Pitfalls

### Pitfall 1: Hydration Mismatch Between Server and Client
**What goes wrong:** App crashes with "Hydration failed" error, or content flashes/changes after page load
**Why it happens:** Server Component renders different HTML than Client Component's first render (e.g., using Date.now(), window checks, random values in render)
**How to avoid:**
- Never use browser-only APIs (window, localStorage, Date.now()) during initial render
- Move client-specific logic into useEffect
- Use suppressHydrationWarning={true} sparingly for unavoidable differences (e.g., timestamps)
- Ensure searchParams are identical between server and client
**Warning signs:** Console errors mentioning "Hydration", "Text content does not match", content flickering on page load

### Pitfall 2: Missing Suspense Boundary with useSearchParams
**What goes wrong:** Entire page/layout client-renders instead of server-rendering, losing performance benefits
**Why it happens:** useSearchParams requires Suspense boundary or Next.js de-opts to client rendering for the entire route segment
**How to avoid:**
- Wrap components using useSearchParams with `<Suspense fallback={<div>Loading...</div>}>`
- Or use Server Components with searchParams prop instead of useSearchParams hook
- Or use nuqs which handles this automatically
**Warning signs:** Pages feel slower, React DevTools shows everything as Client Component, no server-rendered HTML in view source

### Pitfall 3: Infinite Scroll Without Virtual Scrolling (Memory Leak)
**What goes wrong:** After scrolling through 1000+ logs, page becomes sluggish, browser tab crashes or freezes
**Why it happens:** Each log row remains in DOM even when scrolled out of view - memory usage grows unbounded
**How to avoid:**
- Always pair infinite scroll with virtual scrolling (TanStack Virtual)
- Set estimateSize for consistent performance
- Monitor memory usage in browser DevTools during testing
**Warning signs:** Page slows down progressively as user scrolls, memory usage increases linearly, scroll stuttering

### Pitfall 4: Race Conditions in Debounced Search
**What goes wrong:** User types "error", debounced search fires for "err", then "erro", then "error" - but responses arrive out of order, showing wrong results
**Why it happens:** Network responses don't arrive in request order, last response wins regardless of recency
**How to avoid:**
- Cancel previous fetch requests using AbortController
- Use TanStack Query which handles request cancellation automatically
- Compare timestamp/sequence number of responses
**Warning signs:** Search results occasionally don't match input, flickering results, stale data displayed

### Pitfall 5: Using 'use client' Too High in Component Tree
**What goes wrong:** Entire pages become client-rendered, losing Server Component benefits (performance, SEO, security)
**Why it happens:** 'use client' directive makes component and all children Client Components - placing it at layout/page level cascades
**How to avoid:**
- Mark only leaf components as 'use client' (filter sidebar, search input, modal)
- Keep page/layout as Server Components
- Pass Server Components as children/props to Client Components when needed
**Warning signs:** Large bundle size, slow initial page load, no HTML in view source, all components showing "CC" in React DevTools

### Pitfall 6: Filter State Desync Between URL and Component
**What goes wrong:** Browser back button doesn't restore filters, sharing URL doesn't work, refreshing page loses filters
**Why it happens:** Managing filter state in component state (useState) instead of URL search params - state isn't reflected in URL
**How to avoid:**
- Use nuqs for all filter state (search, severity, source, date range, sort, order)
- Never use useState for state that should be shareable/bookmarkable
- Test back button, refresh, direct URL access during development
**Warning signs:** Back button doesn't restore filters, URL doesn't change when filters change, sharing links doesn't preserve filters

### Pitfall 7: Form Submission Without Loading/Error States
**What goes wrong:** User clicks submit multiple times (no feedback), form feels broken, errors are silently swallowed
**Why it happens:** Not tracking loading state, not disabling submit button, not showing validation errors
**How to avoid:**
- Use react-hook-form's formState.isSubmitting to disable button
- Show loading spinner on submit button during submission
- Display validation errors with formState.errors
- Use toast notifications for success/error feedback
- Implement optimistic UI where appropriate
**Warning signs:** Users complain form is "not working", duplicate submissions in logs, no feedback on submission

### Pitfall 8: Importing Server Components Into Client Components
**What goes wrong:** Build fails with error "You're importing a component that needs X. That only works in a Server Component"
**Why it happens:** Client Components cannot import Server Components (but can receive them as props/children)
**How to avoid:**
- Pass Server Components as children or props to Client Components
- Never import Server Components in files with 'use client'
- Restructure to have Server Component wrapper with Client Component islands
**Warning signs:** Build errors mentioning "Server Component", component structure feels awkward, need to fetch data in Client Component

### Pitfall 9: Missing Environment Variable Prefix NEXT_PUBLIC_
**What goes wrong:** API_URL is undefined in browser, API calls fail with CORS/network errors
**Why it happens:** Next.js only exposes env vars starting with NEXT_PUBLIC_ to browser bundle - others are server-only
**How to avoid:**
- Name client-side env vars with NEXT_PUBLIC_ prefix (NEXT_PUBLIC_API_URL)
- Keep server-only secrets (database passwords) without prefix
- Verify env vars in browser console during development
**Warning signs:** Env var is undefined in client code but works in server code, API calls fail with "undefined" URL

### Pitfall 10: Skeleton Loading UI Causes Layout Shift
**What goes wrong:** Page content jumps/shifts when real data loads after skeleton, poor user experience
**Why it happens:** Skeleton dimensions don't match actual content dimensions
**How to avoid:**
- Use exact same dimensions for skeleton as real content (height, padding, margin)
- Test with real data to ensure no layout shift (measure CLS in Lighthouse)
- Use aspect-ratio CSS for images
- Reserve space with min-height for dynamic content
**Warning signs:** Content jumps on load, poor Lighthouse CLS score, user complaints about "page moving around"

## Code Examples

Verified patterns from official sources:

### Persistent Sidebar Layout
```typescript
// app/layout.tsx (Root Layout - Server Component)
import { Sidebar } from '@/components/nav/sidebar'
import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen">
          {/* Sidebar persists across all pages */}
          <Sidebar />

          {/* Page content changes on navigation */}
          <main className="flex-1 p-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}

// components/nav/sidebar.tsx
import Link from 'next/link'

export function Sidebar() {
  return (
    <aside className="w-64 border-r bg-gray-50">
      <nav className="p-4 space-y-2">
        <Link href="/logs" className="block px-4 py-2 rounded hover:bg-gray-200">
          Logs
        </Link>
        <Link href="/create" className="block px-4 py-2 rounded hover:bg-gray-200">
          Create Log
        </Link>
        {/* Dashboard link added in Phase 5 */}
      </nav>
    </aside>
  )
}
```
**Source:** https://nextjs.org/docs/app/building-your-application/routing/layouts-and-templates

### Server Component with Client Component Islands
```typescript
// app/logs/page.tsx (Server Component)
import { Suspense } from 'react'
import { LogList } from './_components/log-list'
import { LogFilters } from './_components/log-filters'
import { SkeletonRows } from './_components/skeleton-rows'

export default async function LogsPage() {
  // Fetch initial data on server
  const initialData = await fetch(
    `${process.env.API_URL}/api/logs?limit=50`,
    { cache: 'no-store' } // Disable cache for always-fresh data
  ).then(r => r.json())

  return (
    <div className="flex gap-6">
      <div className="w-64">
        {/* Client Component for filters */}
        <Suspense fallback={<div>Loading filters...</div>}>
          <LogFilters />
        </Suspense>
      </div>

      <div className="flex-1">
        <h1 className="text-2xl font-bold mb-4">Logs</h1>

        {/* Client Component for interactive list */}
        <Suspense fallback={<SkeletonRows count={10} />}>
          <LogList initialData={initialData} />
        </Suspense>
      </div>
    </div>
  )
}
```
**Source:** https://nextjs.org/docs/app/building-your-application/rendering/client-components

### Severity Badge Component
```typescript
// components/shared/severity-badge.tsx
const severityColors = {
  INFO: 'bg-blue-100 text-blue-800',
  WARNING: 'bg-yellow-100 text-yellow-800',
  ERROR: 'bg-red-100 text-red-800',
  CRITICAL: 'bg-red-900 text-white',
} as const

type Severity = keyof typeof severityColors

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${severityColors[severity]}`}>
      {severity}
    </span>
  )
}
```

### Skeleton Loading State
```typescript
// app/logs/_components/skeleton-rows.tsx
export function SkeletonRows({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 p-4 border rounded animate-pulse">
          <div className="w-20 h-6 bg-gray-200 rounded" /> {/* Severity */}
          <div className="flex-1 h-6 bg-gray-200 rounded" /> {/* Message */}
          <div className="w-32 h-6 bg-gray-200 rounded" /> {/* Timestamp */}
        </div>
      ))}
    </div>
  )
}
```

### Toast Notifications with Sonner
```typescript
// app/layout.tsx (add Toaster to root)
import { Toaster } from 'sonner'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Toaster position="top-right" richColors />
      </body>
    </html>
  )
}

// Usage in any component
'use client'

import { toast } from 'sonner'

export function CreateForm() {
  const handleSubmit = async (data) => {
    try {
      await createLog(data)
      toast.success('Log created successfully!')
    } catch (error) {
      toast.error('Failed to create log. Please try again.')
    }
  }

  return <form onSubmit={handleSubmit}>{/* ... */}</form>
}
```
**Source:** https://sonner.emilkowal.ski

### Environment Variables Setup
```bash
# frontend/.env.local (create this file)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Access in code:
# - Server Components: process.env.API_URL or process.env.NEXT_PUBLIC_API_URL
# - Client Components: process.env.NEXT_PUBLIC_API_URL (must have NEXT_PUBLIC_ prefix)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pages Router | App Router | Next.js 13 (stable in 14, recommended in 15) | Server Components by default, better performance, improved routing patterns |
| react-window | TanStack Virtual | 2023 | Smaller bundle (10kb vs 35kb), more flexible API, better TypeScript support |
| getServerSideProps | Server Components with fetch | Next.js 13 | Simpler API, component-level data fetching, automatic request deduplication |
| CSS-in-JS (styled-components) | Tailwind CSS | 2020-2022 trend shift | Zero runtime overhead, smaller bundles, faster development |
| Manual URLSearchParams | nuqs / next-usequerystate | 2023-2024 | Type-safe, less boilerplate, automatic serialization, framework integration |
| Formik | react-hook-form | 2019-2020 | Better performance (fewer re-renders), smaller bundle, modern API |
| Component libraries (MUI, Chakra) | shadcn/ui (copy-paste components) | 2023-2024 | Full customization, no wrapper overhead, code ownership, AI-friendly |

**Deprecated/outdated:**
- **Pages Router (pages/)**: Still supported but App Router (app/) is now recommended for new projects - better performance, Server Components
- **getServerSideProps/getStaticProps**: Replaced by Server Components with fetch - simpler, more flexible
- **next/router**: Replaced by next/navigation (useRouter, usePathname, useSearchParams) - App Router compatible
- **_app.js/_document.js**: Replaced by layout.tsx/template.tsx - more flexible, composable
- **API routes for data fetching (pages/api/)**: Still valid but Server Components can fetch directly - fewer round-trips

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Jest 29 + React Testing Library 14 (or Vitest 1.x as alternative) |
| Config file | jest.config.js (or vitest.config.ts) — see Wave 0 |
| Quick run command | `npm test -- --testPathPattern=logs --bail` |
| Full suite command | `npm test -- --coverage` |

**Reasoning:** Next.js officially recommends Jest with React Testing Library or Vitest. Jest is more mature with better Next.js integration via next/jest. Vitest is faster but newer. Choose based on team preference.

**Setup:** Next.js provides built-in Jest configuration via `next/jest` which handles:
- Auto-mocking Next.js modules (next/router, next/image, etc.)
- Loading .env.local files
- Ignoring node_modules from transformation
- Loading next.config.js

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| UI-01 | Log list page renders with table, filters, search, sorting, pagination | integration | `npm test tests/logs/log-list.test.tsx` | ❌ Wave 0 |
| UI-02 | Log detail modal opens on row click, displays full log info | integration | `npm test tests/logs/log-detail-modal.test.tsx` | ❌ Wave 0 |
| UI-03 | Log creation form validates input, submits to API | integration | `npm test tests/create/create-form.test.tsx` | ❌ Wave 0 |
| UI-05 | Server Components fetch initial data | integration | `npm test tests/logs/page.test.tsx` | ❌ Wave 0 |
| UI-06 | Client Components handle interactivity (filters, search) | unit | `npm test tests/components/log-filters.test.tsx` | ❌ Wave 0 |
| UI-07 | Loading states display during data fetch | integration | `npm test tests/logs/loading-states.test.tsx` | ❌ Wave 0 |
| UI-08 | Error messages display on API failure | integration | `npm test tests/logs/error-handling.test.tsx` | ❌ Wave 0 |
| UI-09 | Responsive layout works at 768px, 1440px, 1920px | integration | `npm test tests/responsive.test.tsx` | ❌ Wave 0 |
| FILTER-01 | Search input debounces and updates URL | unit | `npm test tests/components/search-input.test.tsx` | ❌ Wave 0 |
| FILTER-02 | Date range filters update URL and fetch filtered logs | integration | `npm test tests/filters/date-range.test.tsx` | ❌ Wave 0 |
| FILTER-03 | Severity multi-select updates URL and fetches filtered logs | integration | `npm test tests/filters/severity.test.tsx` | ❌ Wave 0 |
| FILTER-04 | Source filter updates URL and fetches filtered logs | integration | `npm test tests/filters/source.test.tsx` | ❌ Wave 0 |
| FILTER-05 | Multiple filters combine correctly in API call | integration | `npm test tests/filters/combined.test.tsx` | ❌ Wave 0 |
| FILTER-06 | Sorting by column headers updates URL and refetches | integration | `npm test tests/logs/sorting.test.tsx` | ❌ Wave 0 |
| FILTER-07 | Filter state persists in URL on navigation/refresh | integration | `npm test tests/filters/url-persistence.test.tsx` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `npm test -- --testPathPattern={modified-file} --bail` (test only affected files, exit on first failure)
- **Per wave merge:** `npm test -- --onlyChanged` (test all changed files since last commit)
- **Phase gate:** `npm test -- --coverage --coverageThreshold='{"global":{"statements":70,"branches":60,"functions":70,"lines":70}}'` (full suite with coverage requirements)

### Wave 0 Gaps
- [ ] `tests/setup.ts` — Test environment setup (mock Next.js router, fetch, window.matchMedia)
- [ ] `jest.config.js` — Jest configuration with next/jest preset
- [ ] `tests/mocks/api.ts` — Mock API responses for testing without backend
- [ ] `tests/utils.tsx` — Test utilities (custom render with providers, waitFor helpers)
- [ ] Framework install: `npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event jest-environment-jsdom`

**Notes:**
- Integration tests use React Testing Library to render components and simulate user interactions
- Unit tests focus on individual utilities (debounce, URL parsing, date formatting)
- Mock API responses to avoid backend dependency
- Test responsive behavior using jest-matchmedia-mock or similar
- Use MSW (Mock Service Worker) for advanced API mocking if needed

## Sources

### Primary (HIGH confidence)
- Next.js Documentation (https://nextjs.org/docs) - App Router architecture, Server Components, data fetching patterns, testing
- React Documentation (https://react.dev) - React 19 features, Server Components
- shadcn/ui Documentation (https://ui.shadcn.com/docs) - Installation, component patterns, philosophy
- TanStack Virtual Documentation (https://tanstack.com/virtual/latest) - Virtual scrolling API, patterns
- nuqs Documentation (https://nuqs.dev) - URL state management API, patterns
- React Hook Form Documentation (https://react-hook-form.com) - Form validation patterns, performance characteristics
- Zod Documentation (https://zod.dev) - Schema validation, TypeScript integration
- Sonner Documentation (https://sonner.emilkowal.ski) - Toast notification patterns
- Radix UI Documentation (https://www.radix-ui.com/primitives) - Accessible primitives
- Tailwind CSS Documentation (https://tailwindcss.com/docs) - Next.js setup, utilities

### Secondary (MEDIUM confidence)
- Next.js Error Messages (https://nextjs.org/docs/messages) - Common errors and solutions
- React Testing Library Documentation (https://testing-library.com/docs/react-testing-library/intro) - Testing patterns

### Tertiary (LOW confidence)
- None - all findings verified with official documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified with official docs, versions confirmed, installation tested
- Architecture: HIGH - Patterns from official Next.js/React docs, widely adopted in production
- Pitfalls: HIGH - Verified from official Next.js error messages and documentation, common issues documented
- Testing: HIGH - Official Next.js testing recommendations, standard industry practices

**Research date:** 2026-03-21
**Valid until:** ~30 days (stable stack, but Next.js/React ecosystem updates frequently - verify versions before starting)
