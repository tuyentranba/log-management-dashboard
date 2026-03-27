# ADR-005: Frontend Architecture Patterns and Design Principles

**Status:** Accepted
**Date:** 2026-03-21
**Deciders:** Development Team

## Context

Building a Next.js 15 application with App Router requires making architectural decisions that balance server-side rendering performance with client-side interactivity. Unlike traditional React SPAs where everything is client-side, Next.js 15 introduces Server Components as the default, requiring explicit "use client" directives for interactive components.

### The Problem Space

We need consistent frontend patterns across four key architectural concerns:

**1. Component Boundary Decisions:**
When should we use Server Components vs Client Components? Next.js 15 defaults to Server Components, but interactivity requires Client Components. Drawing the boundary incorrectly leads to either:
- Over-use of Server Components → Loss of interactivity, forced full-page refreshes
- Over-use of Client Components → Loss of SSR benefits, increased JavaScript bundle, slower initial page load

**2. Logic Reusability:**
When should we extract logic into custom hooks vs keep it inline? Every component with `useState`, API calls, or effects faces this question. Extracting too eagerly creates abstraction overhead. Extracting too late creates duplication.

**3. State Management Philosophy:**
Where should UI state live - URL query parameters, React state, Context API, external state library? With a requirement for shareable links (filters must persist in URL), we need a pattern that makes URL the source of truth without sync complexity.

**4. Component Composition:**
How should we structure parent-child relationships? Container/Presenter pattern? Feature-based components? Composition via children props? Each approach has trade-offs for reusability vs cohesion.

### Technical Context

- **Framework:** Next.js 15.5.14 with App Router
- **React Version:** React 19.2.4 (latest)
- **TypeScript:** 5.9.3 for type safety
- **State Management:** `nuqs` library for URL query parameter state
- **Requirement:** Demonstrate technical excellence with clean patterns suitable for portfolio evaluation

### Specific Challenges Encountered

During Phase 3 implementation, we encountered these specific issues:
- **Filter reactivity problem:** Server Component props frozen at initial render, Client Components couldn't react to URL changes (documented in ADR-001)
- **Custom hook duplication:** Filter schema duplicated across 3 components before extracting shared hook
- **Component size:** Some components exceeded 200 lines mixing state, logic, and presentation
- **SSR vs interactivity trade-off:** Forms and modals require client-side state, but we want SSR for initial page load

## Requirements Addressed

- **UI-05:** Frontend uses React Server Components for data fetching
- **UI-06:** Frontend uses Client Components only for interactive features
- **FILTER-07:** Filter state persists when navigating between pages (URL state)
- **NFR-Maintainability:** Consistent patterns enable easy feature additions
- **NFR-Performance:** SSR with selective hydration for fast initial page load

## Topics Covered

This ADR covers four related frontend architectural patterns. Each topic follows a mini-ADR structure (context, options considered, decision, benefits).

---

### Topic 1: Server Components vs Client Components Strategy

#### Context

Next.js 15 App Router defaults to Server Components. All components are server-rendered unless marked with "use client" directive. Decision needed: when should we add "use client"?

This isn't a simple "data fetching = server, interactivity = client" rule. Some components need both (e.g., page that fetches data AND manages filter state). We need clear criteria.

#### Options Considered

**Option A: Client Components Everywhere (Traditional React SPA)**

Use "use client" at the root layout, making entire app client-side like traditional Create React App.

**Pros:**
- Familiar React patterns
- No mental overhead about Server vs Client
- All hooks and state work everywhere

**Cons:**
- Loses SSR performance benefits (slower initial page load)
- Larger JavaScript bundle (all React code shipped to browser)
- No SEO benefits from server-rendered HTML
- Defeats purpose of Next.js 15 architecture

**Option B: Server Components Everywhere with Server Actions**

Use Server Components by default, handle all interactivity via Server Actions (form submissions, mutations).

**Pros:**
- Minimal JavaScript shipped to browser
- Maximum SSR performance
- SEO-friendly for all pages

**Cons:**
- Forces server roundtrips for UI state changes
- Poor UX for instant feedback (modals, filters, form validation)
- Cannot use React hooks (useState, useEffect)
- Server Actions better suited for mutations, not UI state

**Option C: Hybrid - Server for Data, Client for Interactivity** ✓

Use Server Components for data fetching and initial render. Use Client Components for interactivity (forms, modals, filters, infinite scroll).

**Pros:**
- Fast initial page load (SSR HTML)
- Interactive features feel instant (client-side state)
- Follows Next.js 15 best practices
- Clear mental model for when to use each

**Cons:**
- Requires understanding both patterns
- Must carefully place "use client" boundary
- Cannot use hooks in Server Components

#### Decision

**We will use a hybrid approach with explicit criteria for when to use each pattern.**

**Server Components for:**
- Page components (top-level route handlers)
- Layout components (app/layout.tsx)
- Initial data fetching (fetching logs for SSR)
- Static content (headers, footers, navigation)

**Client Components for:**
- Forms with validation (react-hook-form, user input)
- Modals and dialogs (open/close state)
- Filters and search (URL state management)
- Infinite scroll (cursor pagination state)
- Toast notifications (dynamic UI feedback)
- Any component using React hooks (useState, useEffect, custom hooks)

**Data flow pattern:**
```
Server Component (page.tsx)
  ↓ fetches initial data via API
  ↓ passes as props
Client Component (log-list.tsx)
  ↓ renders initial data
  ↓ manages interactive state
  ↓ fetches additional data via client-side API calls
```

#### Examples from Codebase

**Server Component: `app/logs/page.tsx`**
```typescript
// No "use client" - this is a Server Component
export default async function LogsPage({ searchParams }) {
  // Fetch initial data on server (SSR)
  const initialData = await fetchLogs(filters, null, 50)

  return (
    <div>
      <LogFiltersComponent />
      <LogsPageContent initialData={initialData} />
    </div>
  )
}
```

**Client Component: `_components/log-list.tsx`**
```typescript
'use client'  // Explicit directive for interactivity

export function LogList({ initialData }) {
  const [filters, setFilters] = useLogFilters()  // URL state hook
  const { logs, loadMore } = useInfiniteScroll(initialData)  // Pagination hook

  // Interactive state management, event handlers, etc.
}
```

**Server Component: `app/analytics/page.tsx`**
```typescript
// Server Component for initial SSR
export default async function AnalyticsPage({ searchParams }) {
  const analyticsData = await fetchAnalytics(...)
  return <AnalyticsContent initialData={analyticsData} />
}
```

**Client Component: `_components/time-range-filter.tsx`**
```typescript
'use client'  // Needs useState for date picker state

export function TimeRangeFilter() {
  const [dateFrom, setDateFrom] = useQueryState('date_from')
  // Interactive date selection, URL state updates
}
```

#### Benefits

- **Fast initial page load:** Server-rendered HTML displays instantly (no JavaScript required for first paint)
- **Instant interactivity:** Client-side state changes feel immediate (no server roundtrip)
- **Reduced JavaScript bundle:** Only interactive components ship React code to browser
- **SEO-friendly:** Search engines see fully-rendered HTML
- **Progressive enhancement:** Page works without JavaScript (initial render), then enhances with interactivity

---

### Topic 2: Custom Hooks Pattern (When to Extract Logic)

#### Context

Reusable logic appears across multiple components: filter state management, pagination cursors, API fetching, form validation. We need criteria for when to extract logic into custom hooks vs keep it inline.

Premature abstraction creates complexity without benefit. Late abstraction creates duplication. We need the "Goldilocks zone."

#### Options Considered

**Option A: Extract All Logic to Hooks (Maximum Reusability)**

Create custom hooks for every piece of logic: `useModalState()`, `useFormValidation()`, `useApiCall()`, etc.

**Pros:**
- Maximum reusability
- Clear separation of concerns
- Easy to test in isolation

**Cons:**
- Abstraction overhead (more files, imports, indirection)
- Premature optimization for single-use logic
- Harder to understand (logic split across files)

**Option B: Keep Logic Inline in Components (Simplicity)**

Never extract custom hooks. Keep all logic inside component files.

**Pros:**
- Simple to understand (all logic in one place)
- No file navigation needed
- No abstraction complexity

**Cons:**
- Duplication across components
- Harder to test complex logic
- Components become large and unwieldy

**Option C: Extract When Meets Criteria (Pragmatic)** ✓

Extract to custom hook when logic meets ANY of these criteria:
1. **Reused in 2+ components**
2. **Complex enough to warrant independent testing**
3. **Represents a distinct concern** (state management, data fetching, side effects)

**Pros:**
- Balances reusability with simplicity
- Clear criteria for when to extract
- Avoids premature abstraction

**Cons:**
- Requires judgment calls
- May refactor inline → hook later (acceptable)

#### Decision

**We will extract logic to custom hooks when it meets extraction criteria (reused 2+ times, complex, or distinct concern).**

**Extraction criteria:**
1. **Reused in 2+ components** - DRY principle applies
2. **Complex state machine** - Independent testing valuable
3. **Distinct concern** - Clear separation of responsibilities

**DO extract these patterns:**
- **Filter state management** (`use-log-filters.ts`) - Used in LogList, LogFilters, useInfiniteScroll (3+ components)
- **Pagination logic** (`use-infinite-scroll.ts`) - Complex state machine (cursor, hasMore, isLoading), warrants testing
- **Form validation logic** - If shared across multiple forms (create, edit, search)

**DO NOT extract these patterns:**
- **Simple useState toggles** - Modal open/close state (`const [isOpen, setIsOpen] = useState(false)`)
- **Single-use API calls** - Inline `useEffect` with `fetchData()` if only used once
- **Simple computed values** - Deriving display text from props

#### Examples from Codebase

**Custom Hook: `use-log-filters.ts` (Extracted - Used in 3+ Components)**
```typescript
// Shared across LogList, LogFilters, useInfiniteScroll
export function useLogFilters() {
  return useQueryStates(logFiltersSchema)
}
```

**Custom Hook: `use-infinite-scroll.ts` (Extracted - Complex State Machine)**
```typescript
// Complex pagination logic with cursor, isLoading, hasMore state
export function useInfiniteScroll(initialData) {
  const [logs, setLogs] = useState(initialData.data)
  const [cursor, setCursor] = useState(initialData.next_cursor)
  const [hasMore, setHasMore] = useState(initialData.has_more)
  const [isLoading, setIsLoading] = useState(false)

  // Complex useEffect watching filters, refetching logic
  useEffect(() => { /* ... */ }, [filtersKey])

  return { logs, hasMore, isLoading, loadMore, refetch }
}
```

**Inline Logic: Modal State (NOT Extracted - Simple Single-Use)**
```typescript
export function LogDetailModal() {
  // Simple toggle - not worth extracting
  const [isEditing, setIsEditing] = useState(false)
}
```

**Inline Logic: Form Validation (NOT Extracted - react-hook-form Handles It)**
```typescript
export function CreateForm() {
  // react-hook-form already provides validation hooks
  const { register, handleSubmit, formState: { errors } } = useForm()
  // No need for custom useFormValidation() hook
}
```

#### Benefits

- **DRY principle for genuinely reusable logic** - Avoid duplication across components
- **Testable in isolation** - Complex hooks can have dedicated test files
- **Clear separation of concerns** - State management separated from presentation
- **Avoids premature abstraction** - Don't extract until criteria met
- **Easier to refactor** - Hook logic can be changed without touching components

---

### Topic 3: URL State Management Philosophy (Single Source of Truth)

#### Context

Filter state, modal state, and date ranges need to persist in URL for shareable links (requirement FILTER-07). We need a pattern for managing URL state that avoids synchronization bugs.

The challenge: React state and URL params can get out of sync. User updates filter → writes to URL → needs to read from URL → but component has stale React state. This was the bug documented in ADR-001.

#### Options Considered

**Option A: React State Synced to URL with useEffect (Two-Way Sync)**

Keep filter state in React useState, sync to URL with useEffect. Read URL on mount, write to URL on state change.

**Pros:**
- Familiar React pattern
- State feels "immediate" (setState)

**Cons:**
- **Sync bugs:** React state and URL can diverge
- **Complex useEffect logic:** Watch state → update URL, watch URL → update state
- **Race conditions during hydration:** Which takes precedence, URL or state?
- **Doesn't eliminate root cause:** Still two sources of truth

**Option B: Context/Zustand State with URL as Secondary**

Store filter state in React Context or Zustand, persist to URL as secondary concern.

**Pros:**
- Centralized state management
- Easy to access anywhere in component tree

**Cons:**
- **URL not source of truth:** Shareable links don't work until context hydrates
- **Complex sync logic:** Context ↔ URL synchronization needed
- **Additional dependency:** Zustand adds 1kb+ to bundle

**Option C: URL as Single Source of Truth (nuqs Library)** ✓

Make URL the canonical state store. All components read/write directly to URL query parameters using `nuqs` library. No separate React state for URL-persisted values.

**Pros:**
- **Single source of truth:** URL is the state, no sync needed
- **Shareable links work automatically:** URL contains all filter state
- **React hooks interface:** `useQueryStates` feels like `useState`
- **No sync bugs:** Can't get out of sync when there's only one source

**Cons:**
- **Requires client component:** Cannot use in Server Components (acceptable trade-off)
- **Learning curve:** Team needs to understand nuqs reactivity model
- **Dependency:** nuqs library (small, 2kb gzipped, well-maintained)

#### Decision

**We will use URL as single source of truth for all shareable state using the `nuqs` library.**

**Pattern:**
```typescript
// All components read/write same URL state
const [filters, setFilters] = useLogFilters()

// Read current URL params
console.log(filters.severity)  // ['ERROR', 'CRITICAL']

// Write to URL (triggers re-render in all consuming components)
setFilters({ severity: ['INFO'] })
```

**State flow:**
```
User clicks filter checkbox
  ↓
LogFilters component calls setFilters()
  ↓
nuqs updates URL (?severity=INFO)
  ↓
useQueryStates hook in all components detects change
  ↓
LogList re-renders with new filters
  ↓
FilterChips recompute and display correctly
  ↓
useInfiniteScroll useEffect detects change
  ↓
API refetch triggered with new filters
```

**Implementation:**
```typescript
// Shared hook ensures consistency
export function useLogFilters() {
  return useQueryStates({
    search: parseAsString,
    severity: parseAsArrayOf(parseAsString),
    source: parseAsString,
    date_from: parseAsString,
    date_to: parseAsString,
    sort: parseAsString.withDefault('timestamp'),
    order: parseAsString.withDefault('desc'),
  })
}
```

#### Benefits

- **Shareable links work automatically:** Copy URL → share → recipient sees exact same filters
- **No sync bugs:** Single source of truth eliminates React state ↔ URL divergence
- **History back/forward works:** Browser navigation respects filter state changes
- **Component reactivity:** All components using `useLogFilters()` react to URL changes instantly
- **Simple mental model:** URL is the state, read/write just like React state

#### Detailed Rationale

See **ADR-001 (Filter Reactivity Refactor)** for comprehensive exploration of this decision, including:
- Root cause of initial Server Component prop staleness bug
- Comparison of 4 alternative approaches with code examples
- Migration path from prop-based to URL-based state
- Performance implications and trade-offs

This ADR (005) documents the architectural principle. ADR-001 documents the specific refactoring that discovered and solved the problem.

---

### Topic 4: Component Composition Patterns

#### Context

Components need to be composable and maintainable. As features grow, we need patterns for structuring parent-child relationships and deciding when to split components.

#### Options Considered

**Option A: Container/Presenter Pattern (Smart/Dumb Components)**

Separate all components into Container (logic) and Presenter (UI) pairs.

**Pros:**
- Clear separation of concerns
- Presenters highly reusable
- Easy to test presenters (pure functions)

**Cons:**
- Doubles number of files
- Artificial separation when logic and UI tightly coupled
- Outdated pattern (modern React hooks reduce need)

**Option B: Feature-Based Components (Cohesion Over Separation)**

Keep related logic and UI together in single component.

**Pros:**
- Easier to understand (all logic in one place)
- Less file navigation
- Natural cohesion

**Cons:**
- Components can become large
- Harder to reuse presentation logic
- Mixing concerns in single file

**Option C: Composition via Children/Slots (Maximum Flexibility)**

Use children props and composition patterns for all layout.

**Pros:**
- Very flexible
- No prop drilling
- Reusable layout components

**Cons:**
- Can be overused (too abstract)
- Harder to understand data flow
- Sometimes prop drilling is clearer

**Option D: Pragmatic Hybrid (Context-Driven)** ✓

Use different patterns based on context:
- Presentation components for pure rendering (SeverityBadge)
- Feature components when state/logic tightly coupled (LogDetailModal)
- Composition via children for layout flexibility (Card, Dialog)

**Pros:**
- Flexibility to choose right pattern
- Balances reusability with simplicity
- Clear criteria for when to split

**Cons:**
- Requires judgment
- Less dogmatic (team must understand trade-offs)

#### Decision

**We will use pragmatic composition patterns based on component needs:**

**1. Presentation Components (Pure Rendering)**
For components that transform props to JSX with no internal state.

**Example: SeverityBadge**
```typescript
export function SeverityBadge({ severity }: { severity: Severity }) {
  const colors = {
    INFO: 'bg-blue-500',
    WARNING: 'bg-yellow-500',
    ERROR: 'bg-orange-600',
    CRITICAL: 'bg-red-600'
  }
  return <span className={colors[severity]}>{severity}</span>
}
```

**Characteristics:**
- No internal state (useState)
- Pure props → JSX transformation
- Highly reusable across pages
- Easy to test (snapshot testing)

**2. Feature Components (Logic + Presentation Coupled)**
For components where state and rendering are tightly coupled.

**Example: LogDetailModal**
```typescript
export function LogDetailModal({ logId }) {
  const [isEditing, setIsEditing] = useState(false)  // State
  const log = useFetchLog(logId)  // Data fetching

  // Tightly coupled: edit state only makes sense with modal UI
  return (
    <Dialog>
      {isEditing ? <EditForm /> : <LogDetails />}
    </Dialog>
  )
}
```

**Characteristics:**
- State and UI tightly coupled
- State doesn't make sense outside component
- Logic specific to this feature
- Splitting would create artificial separation

**3. Composition via Children (Layout Flexibility)**
For reusable layout components that don't care about content.

**Example: Card Component**
```typescript
export function Card({ children, title }) {
  return (
    <div className="border rounded p-4">
      {title && <h3>{title}</h3>}
      {children}
    </div>
  )
}

// Usage:
<Card title="Filters">
  <FilterForm />
</Card>
```

**Characteristics:**
- Layout wrapper
- Content-agnostic
- Reusable across features

#### When to Split Components

**DO split when:**
- Component exceeds 200 lines
- Component has multiple distinct responsibilities (violates Single Responsibility Principle)
- Presentation is reusable elsewhere (severity badge, date formatter)
- Need to test presentation independent of logic

**DON'T split when:**
- State and rendering tightly coupled (modal with form)
- Component < 100 lines and cohesive
- Only used in one place
- Splitting creates artificial separation

#### Benefits

- **Reusable presentation components:** SeverityBadge, Card, Button used across pages
- **Cohesive feature components:** Complex features keep related logic together
- **Flexible composition:** Layout components accept children for flexibility
- **Pragmatic splitting:** Split when it adds value, not dogmatically

---

## Consequences

### Positive

1. **Consistent patterns across entire frontend codebase:** New developers can predict component structure, reducing onboarding time.

2. **New features follow established patterns:** Adding a new filter component? Use `useLogFilters()` hook. Adding a new page? Server Component with Client Component islands.

3. **SSR performance benefits:** Fast initial page load (< 1 second), SEO-friendly server-rendered HTML, reduced JavaScript bundle size.

4. **URL state enables shareable links:** Requirement FILTER-07 satisfied. Users can bookmark or share filtered views.

5. **Custom hooks testable independently:** `use-infinite-scroll.ts` can have dedicated test file without rendering full component tree.

6. **Clear mental model for each pattern:** Team has explicit criteria for when to use Server vs Client, when to extract hooks, when to split components.

7. **Reduced decision fatigue:** Patterns documented, developers don't re-debate "should I use Server Component?" on every feature.

8. **Maintainable codebase:** Consistent patterns make refactoring predictable (change hook implementation, all consumers update automatically).

### Negative

1. **Learning curve for Next.js 15 Server/Client Component model:** Team members must understand difference, when to use "use client", prop passing limitations.

2. **nuqs library introduces dependency:** Adds 2kb gzipped to bundle. Well-maintained library (active development, good docs) but still external dependency.

3. **Some duplication accepted to avoid premature abstraction:** We don't extract every piece of logic to hooks immediately. Initial duplication acceptable until reuse pattern emerges.

4. **Pattern documentation needed:** This ADR serves as onboarding material. New developers must read to understand conventions. Without documentation, patterns feel arbitrary.

5. **Judgment calls required:** "Should I split this component?" isn't always clear-cut. 150-line component in gray area between "too small to split" and "too large to maintain."

6. **Refactoring overhead when patterns change:** If we discover better pattern, must update multiple components. Consistency means changes propagate widely.

### Neutral

1. **Patterns evolve as framework evolves:** Next.js 15 → 16 may change Server Component behavior. We'll adapt patterns as framework best practices evolve.

2. **Trade-offs between patterns sometimes unclear:** Container vs Feature component boundary not always obvious. We document edge cases as encountered.

3. **TypeScript adds boilerplate:** Custom hooks need type exports, props need interface definitions. More lines of code but better safety.

## Alternatives Rejected

### Why Not Full Client-Side (SPA)?

**Rejected because it loses SSR performance benefits.**

**Concrete example:**
Traditional React SPA (Create React App style):
1. Browser requests `/logs`
2. Server returns empty HTML with `<div id="root"></div>`
3. Browser downloads 200kb+ JavaScript bundle
4. React initializes, component mounts
5. useEffect fires, fetch API call
6. Logs display

**Total time to first content:** 2-3 seconds (network + parse + execute + fetch + render)

Next.js 15 Server Components:
1. Browser requests `/logs`
2. Server fetches logs from API (server-side, fast internal network)
3. Server renders HTML with actual log data
4. Browser displays HTML immediately

**Total time to first content:** 300-500ms (server render + HTML transfer)

**Why rejected:** Requirement UI-05 mandates Server Components for data fetching. Initial page load speed critical for user experience. Client-only loses 1.5-2 second performance advantage.

### Why Not Full Server Components with Server Actions?

**Rejected because it forces server roundtrips for UI state changes.**

**Concrete example:**
Modal open/close with Server Actions:
1. User clicks "Edit" button
2. Server Action called (POST request to server)
3. Server re-renders component tree
4. HTML streamed back to client
5. Modal appears

**Latency:** 50-100ms per interaction (network roundtrip)

Modal open/close with Client Component:
1. User clicks "Edit" button
2. `setIsEditing(true)` updates local state
3. Modal appears

**Latency:** < 5ms (pure client-side state update)

**Why rejected:** Requirement UI-06 mandates Client Components for interactive features. Filter checkbox toggles, modal open/close, form validation should feel instant. Server Actions add unacceptable latency for UI state changes. Server Actions better suited for mutations (database updates), not UI state (modal visibility).

### Why Not Context/Zustand for Filter State?

**Rejected because URL must be source of truth for shareable links (FILTER-07).**

**Problem with Context approach:**
```typescript
// Filter state in React Context
const [filters, setFilters] = useState({ severity: ['ERROR'] })

// User applies filter
setFilters({ severity: ['INFO'] })

// URL out of sync: ?severity=ERROR
// User copies URL, shares with colleague
// Colleague opens link → sees ERROR filter (wrong!)
```

**Sync attempt with useEffect:**
```typescript
// Watch filters, update URL
useEffect(() => {
  setSearchParams(filters)
}, [filters])

// Watch URL, update filters
useEffect(() => {
  setFilters(parseSearchParams())
}, [searchParams])
```

**Problems:**
- Two sources of truth (React state and URL)
- Race condition: which useEffect fires first?
- Infinite loop risk: setState → URL updates → setState → ...
- Hydration mismatch: URL has one value, Context has another

**Why rejected:** ADR-001 documents attempted prop-based approach and sync bugs encountered. nuqs solves this cleanly by making URL the state store, eliminating synchronization entirely. Requirement FILTER-07 mandates URL persistence, making URL-first architecture natural choice.

### Why Not Extract All Logic to Hooks?

**Rejected because it creates abstraction overhead for simple cases.**

**Example: Modal open/close state**
```typescript
// Inline (simple, clear):
const [isOpen, setIsOpen] = useState(false)

// Extracted (unnecessary):
// File: hooks/use-modal-state.ts
export function useModalState(initialOpen = false) {
  const [isOpen, setIsOpen] = useState(initialOpen)
  return { isOpen, open: () => setIsOpen(true), close: () => setIsOpen(false) }
}

// Usage:
const { isOpen, open, close } = useModalState()
```

**Analysis:**
- **Abstraction cost:** New file, import statement, indirection
- **Benefit:** Zero - not reused, not complex enough to test independently
- **Result:** 10 lines of code (hook + import) to replace 1 line

**When is extraction worth it?**
When hook is:
- Reused in 2+ components (DRY principle)
- Complex state machine (useInfiniteScroll with cursor, isLoading, hasMore)
- Distinct concern (filter management across multiple components)

**Why rejected:** Premature abstraction is as harmful as duplication. We extract when extraction criteria met, not reflexively. Simple useState calls stay inline.

## References

### Pattern Examples
- **Server Component:** `frontend/src/app/logs/page.tsx` (fetches initial logs via SSR)
- **Client Component:** `frontend/src/app/logs/_components/log-list.tsx` (manages interactive state)
- **Custom Hook:** `frontend/src/hooks/use-infinite-scroll.ts` (complex pagination logic)
- **Custom Hook:** `frontend/src/hooks/use-log-filters.ts` (shared filter state schema)
- **Presentation Component:** `frontend/src/app/logs/_components/severity-badge.tsx` (pure rendering)
- **Feature Component:** `frontend/src/app/logs/_components/log-detail-modal.tsx` (state + UI coupled)

### Related ADRs
- **ADR-001 (Filter Reactivity Refactor):** Deep dive on URL state management decision, documents filter reactivity bug and solution
- **Plan 03-01, Plan 03-02, Plan 03-03 in STATE.md:** Frontend implementation decisions during Phase 3

### External Documentation
- [Next.js 15 Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components) - Official Next.js documentation on Server Components vs Client Components
- [Next.js 15 Client Components](https://nextjs.org/docs/app/building-your-application/rendering/client-components) - When to use "use client" directive
- [React 19 Documentation](https://react.dev/reference/react) - Latest React patterns and hooks
- [nuqs Library](https://nuqs.47ng.com/) - URL state management library documentation
- [React Hooks Best Practices](https://react.dev/learn/reusing-logic-with-custom-hooks) - When to extract custom hooks

### Architecture Context
This decision integrates with:
- **ADR-001:** Detailed rationale for URL state management (nuqs pattern)
- **ADR-004:** Timezone handling (frontend converts UTC to local timezone for display)
