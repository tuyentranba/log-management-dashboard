# ADR-001: Client-Side Filter State Management with URL as Source of Truth

**Status:** Accepted
**Date:** 2026-03-22
**Deciders:** Development Team

## Context

During Phase 3 implementation (Log Management UI), we discovered a critical reactivity issue with the filter system:

### The Problem

When users interacted with filters (checkboxes for severity, search input, date range), the URL would update correctly via `nuqs`, but the UI did not react to these changes:

1. **FilterChips did not update** - The active filter chips displayed stale state
2. **Log list did not refetch** - New filter selections didn't trigger API calls
3. **FilterChip removal was buggy** - Clicking "X" on a chip read from stale state, potentially overwriting user changes

### Root Cause

The architecture relied on a Server Component (`page.tsx`) passing a `filters` prop to Client Components (`LogList`, `useInfiniteScroll`):

```
Server Component (page.tsx)
  ↓ props (frozen at server render)
Client Components (LogList, useInfiniteScroll)
  ↓ compute state from stale props
UI never updates when URL changes
```

**Why this failed:**
- Next.js 15 Server Components only execute on initial page load and full navigation
- Client-side URL changes (via `nuqs` router) don't trigger Server Component re-execution
- Props passed to Client Components remain frozen at their initial values
- Client Components computing state from props couldn't react to URL changes

### Technical Context

- **Framework:** Next.js 15 with App Router
- **State Management:** `nuqs` for URL query parameter state
- **Pattern:** Server Components for initial SSR, Client Components for interactivity
- **Requirement:** All filter state must persist in URL for shareability

## Decision

**Refactor all filter-consuming components to read state directly from the URL using `nuqs` hooks, eliminating the stale props pattern.**

### Implementation Changes

**0. Create Shared Hook `use-log-filters.ts`:**

To avoid schema duplication across 3+ components, extract the filter state logic into a shared hook:

```typescript
// frontend/src/hooks/use-log-filters.ts
import { useQueryStates, parseAsString, parseAsArrayOf } from 'nuqs'

const logFiltersSchema = {
  search: parseAsString,
  severity: parseAsArrayOf(parseAsString),
  source: parseAsString,
  date_from: parseAsString,
  date_to: parseAsString,
  sort: parseAsString.withDefault('timestamp'),
  order: parseAsString.withDefault('desc'),
}

export function useLogFilters() {
  return useQueryStates(logFiltersSchema)
}

// Optional: Export type for reuse
export type LogFiltersState = ReturnType<typeof useLogFilters>[0]
```

**Benefits of shared hook:**
- Single source of truth for filter schema
- Add new filter = change one place
- Type safety guaranteed consistent
- Can add helper methods (clearFilters, hasActiveFilters)

**1. `use-infinite-scroll.ts` Hook:**
```typescript
// Before: Received filters as parameter
export function useInfiniteScroll(initialData, filters) { ... }

// After: Uses shared hook
import { useLogFilters } from '@/hooks/use-log-filters'

export function useInfiniteScroll(initialData) {
  const [filters] = useLogFilters()
  // useEffect watches URL-derived values
}
```

**2. `log-list.tsx` Component:**
```typescript
// Before: Received filters as prop, had write-only nuqs
export function LogList({ initialData, filters }: LogListProps) {
  const [, setFilters] = useQueryStates({ ... })
  const activeFilters = computeFrom(filters) // stale!

  onRemove: () => {
    const newSeverity = filters.severity.filter(...) // stale!
  }
}

// After: Uses shared hook
import { useLogFilters } from '@/hooks/use-log-filters'

export function LogList({ initialData }: LogListProps) {
  const [filters, setFilters] = useLogFilters()
  const activeFilters = computeFrom(filters) // reactive!

  onRemove: () => {
    const newSeverity = filters.severity.filter(...) // current!
  }
}
```

**3. `log-filters.tsx` Component:**
```typescript
// Before: Defined schema inline
export function LogFilters() {
  const [filters, setFilters] = useQueryStates({ ... schema ... })
}

// After: Uses shared hook
import { useLogFilters } from '@/hooks/use-log-filters'

export function LogFilters() {
  const [filters, setFilters] = useLogFilters()
}
```

**4. `page.tsx` Server Component:**
```typescript
// Before: Passed filters prop
<LogList initialData={...} filters={parsed} />

// After: Only passes initial data
<LogList initialData={...} />
```

### New Data Flow

```
User clicks filter checkbox
  ↓
LogFilters updates URL via nuqs
  ↓
useQueryStates in all components detect change
  ↓
LogList re-renders with new filters
  ↓
FilterChips recompute and display correctly
  ↓
useInfiniteScroll useEffect detects change
  ↓
API refetch triggered with new filters
```

## Consequences

### Positive

1. **Real-time UI updates** - All components react instantly to filter changes
2. **Single source of truth** - URL is the canonical state, eliminating sync issues
3. **Fixes removal bug** - FilterChip onRemove reads current URL state, not stale props
4. **Better React patterns** - Components subscribe to state changes properly
5. **Maintains SSR benefits** - Server Component still fetches initial data for performance
6. **Shareable URLs work** - Filters in URL correctly hydrate on page load

### Negative

1. **Client-only pattern** - All filter consumers must be Client Components
2. **Migration effort** - Required refactoring 4 files (3 components + 1 new shared hook)
3. **Learning curve** - Team needs to understand nuqs reactivity model
4. **Abstraction overhead** - Shared hook adds one layer of indirection

### Technical Debt

- May need optimization if filter state becomes more complex (memoization, debouncing)
- Consider adding helper methods to shared hook (clearFilters, hasActiveFilters) in future iterations

## Alternatives Considered

### 1. Force Full Page Refresh on Filter Change

**Description:** Use Next.js router.push() to trigger full page reload when filters change.

**Rejected because:**
- Terrible user experience (page flickers, loses scroll position)
- Defeats purpose of client-side filtering
- Unnecessarily slow (full server roundtrip)

### 2. Client-Side State Management (Zustand/Context)

**Description:** Move filter state to Zustand store or React Context, keep in sync with URL.

**Rejected because:**
- Loses URL as source of truth (shareability requirement)
- Adds complexity of two-way synchronization (store ↔ URL)
- Introduces additional dependency
- `nuqs` already provides URL state management

### 3. Hybrid: Sync Prop with URL via useEffect

**Description:** Keep Server Component prop pattern, add useEffect to sync with URL changes.

**Rejected because:**
- Complex: requires watching URL, comparing to prop, merging states
- Race condition risks during hydration
- Still requires Client Components to manage state
- Doesn't eliminate the root cause (prop staleness)

### 4. Use Server Actions for Filter Updates

**Description:** Send filter changes to Server Actions, trigger server-side re-render.

**Rejected because:**
- Slower than client-side updates (network roundtrip)
- Doesn't work with URL state requirement
- Overkill for simple filter toggling
- Server Actions better suited for mutations, not UI state

## References

- **Phase 3 Execution:** `.planning/phases/03-log-management-ui/`
- **Affected Files:**
  - `frontend/src/app/logs/page.tsx`
  - `frontend/src/app/logs/_components/log-list.tsx`
  - `frontend/src/hooks/use-infinite-scroll.ts`
- **Related Commits:**
  - `823300f` - Fix: Add NuqsAdapter for URL state management
  - `0d10b41` - Fix: Add filter change detection to useInfiniteScroll
  - `c9e24cf` - Fix: Skip initial mount refetch
  - `0d707fb` - Fix: Parse comma-separated severity in page.tsx
- **External Resources:**
  - [nuqs Documentation](https://nuqs.47ng.com/)
  - [Next.js 15 Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
  - [React Hooks: useEffect Dependencies](https://react.dev/reference/react/useEffect#specifying-reactive-dependencies)

## Implementation Status

- [x] ADR created and approved
- [ ] Create shared hook `use-log-filters.ts`
- [ ] Refactor `log-filters.tsx` to use shared hook
- [ ] Refactor `use-infinite-scroll.ts` to use shared hook
- [ ] Refactor `log-list.tsx` to use shared hook
- [ ] Update `page.tsx` to remove filters prop
- [ ] Test filter selection reactivity
- [ ] Test FilterChip removal
- [ ] Test URL sharing and hydration
- [ ] Commit implementation
