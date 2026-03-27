---
phase: 07-documentation
plan: 02
subsystem: documentation
tags: [adr, design-decisions, documentation, timezone, frontend-architecture]
status: complete
completed_at: 2026-03-27T08:39:52Z

dependency_graph:
  requires: []
  provides:
    - "ADR-004: Timezone handling with timestamptz + UTC normalization"
    - "ADR-005: Frontend architecture patterns (Server/Client, hooks, URL state, composition)"
  affects:
    - "docs/decisions/004-timezone-handling.md"
    - "docs/decisions/005-frontend-architecture.md"

tech_stack:
  added: []
  patterns:
    - "ADR extended template with 7 sections"
    - "Multi-topic ADR structure for related patterns"
    - "Concrete code examples from codebase"
    - "Cross-referencing between ADRs"

key_files:
  created:
    - path: "docs/decisions/004-timezone-handling.md"
      purpose: "Documents timezone handling strategy (timestamptz + UTC normalization)"
      lines: 433
    - path: "docs/decisions/005-frontend-architecture.md"
      purpose: "Documents 4 frontend architecture patterns and principles"
      lines: 802
  modified: []

decisions:
  - "Use ADR-004 to document timezone correctness strategy (timestamptz + UTC normalization)"
  - "Use ADR-005 to cover 4 related frontend topics in single ADR (Server/Client, hooks, URL state, composition)"
  - "Include concrete code examples from actual codebase in both ADRs"
  - "Cross-reference ADR-005 → ADR-001 for detailed URL state management rationale"
  - "Map ADRs to specific requirements (DB-02, ANALYTICS-07, UI-05, UI-06, FILTER-07)"

metrics:
  duration_seconds: 596
  tasks_completed: 2
  files_created: 2
  commits: 2
  lines_written: 1235
---

# Phase 07 Plan 02: Design Decision ADRs Summary

**One-liner:** Created ADR-004 documenting timezone handling (timestamptz + UTC) and ADR-005 covering 4 frontend architecture patterns (Server/Client split, custom hooks, URL state, composition), bringing total ADR count to 5.

## What Was Built

### Task 1: ADR-004 for Timezone Handling Decision
Created comprehensive ADR documenting the decision to use PostgreSQL `timestamptz` with UTC normalization for timezone correctness.

**Sections covered:**
1. **Context:** Problem of timezone ambiguity, analytics aggregation bugs, DST transition issues
2. **Requirements Addressed:** DB-02, ANALYTICS-07, NFR-Correctness, API-07
3. **Options Considered:** 4 alternatives (naive timestamps, local timezone storage, UTC normalization, dual-column storage)
4. **Decision:** timestamptz column with UTC storage, Pydantic validation, frontend conversion
5. **Consequences:** Positive (correct aggregations, standard practice), Negative (original timezone lost), Neutral (PostgreSQL semantics)
6. **Alternatives Rejected:** Why naive timestamps and dual-column storage didn't fit
7. **References:** Implementation files, test coverage, related decisions, external docs

**Key examples:**
- Concrete bug scenario: "3 PM" ambiguous without timezone (PST vs UTC vs JST = 8-17 hour gap)
- Analytics aggregation problem: date_trunc() bucketing logs 17 hours apart together
- PostgreSQL behavior: timestamptz stores UTC internally, converts on input

**File:** `docs/decisions/004-timezone-handling.md` (433 lines)

### Task 2: ADR-005 for Frontend Architecture Patterns
Created multi-topic ADR documenting 4 related frontend architectural patterns and design principles.

**Topics covered:**

**1. Server Components vs Client Components Strategy:**
- Context: Next.js 15 defaults to Server Components, when to use "use client"?
- Decision: Hybrid approach - Server for data fetching, Client for interactivity
- Examples: `app/logs/page.tsx` (Server), `_components/log-list.tsx` (Client)
- Benefits: Fast SSR, instant interactivity, reduced JavaScript bundle

**2. Custom Hooks Pattern (When to Extract Logic):**
- Context: When to extract to custom hook vs keep inline?
- Decision: Extract when meets criteria (reused 2+ times, complex, distinct concern)
- Examples: `use-log-filters.ts` (extracted), modal state (inline)
- Benefits: DRY principle, testable in isolation, avoids premature abstraction

**3. URL State Management Philosophy (Single Source of Truth):**
- Context: Filter state must persist in URL for shareable links (FILTER-07)
- Decision: URL as single source of truth using nuqs library
- Cross-reference: ADR-001 for detailed rationale and filter reactivity bug story
- Benefits: No sync bugs, shareable links automatic, history back/forward works

**4. Component Composition Patterns:**
- Context: How to structure parent-child relationships?
- Decision: Pragmatic hybrid - presentation components, feature components, composition via children
- Examples: SeverityBadge (presentation), LogDetailModal (feature), Card (composition)
- Benefits: Reusable presentation, cohesive features, flexible composition

**Requirements mapped:**
- UI-05: Frontend uses React Server Components for data fetching
- UI-06: Frontend uses Client Components only for interactive features
- FILTER-07: Filter state persists in URL
- NFR-Maintainability: Consistent patterns enable easy feature additions
- NFR-Performance: SSR with selective hydration

**File:** `docs/decisions/005-frontend-architecture.md` (802 lines)

## Requirements Addressed

### DOC-03: Architectural Design Decisions (ADRs)
- **Before:** 3 ADRs exist (001-003)
- **After:** 5 ADRs exist (001-005)
- **Status:** ✅ Fully addressed

**ADR collection now covers:**
1. ADR-001: Client-side filter state management with URL as source of truth
2. ADR-002: Cursor-based pagination for efficient log list rendering (Plan 07-01)
3. ADR-003: Database indexing strategy with BRIN + B-tree composite (Plan 07-01)
4. ADR-004: Timezone handling with timestamptz + UTC normalization (This plan)
5. ADR-005: Frontend architecture patterns and design principles (This plan)

**Architectural coverage:**
- Backend data layer: Timezone handling (004), indexing (003)
- Backend API layer: Pagination (002)
- Frontend state: URL state management (001)
- Frontend architecture: Component patterns (005)

## Deviations from Plan

None - plan executed exactly as written.

## Technical Decisions

### 1. ADR-004 Structure
**Decision:** Follow extended ADR template with 7 sections (Context, Requirements, Options, Decision, Consequences, Alternatives Rejected, References).

**Rationale:** Matches ADR-001 structure for consistency. Each section serves specific purpose:
- Context explains problem space with concrete examples
- Requirements maps to system requirements (traceability)
- Options provides honest comparison of alternatives
- Decision documents what we chose and why
- Consequences lists trade-offs (positive, negative, neutral)
- Alternatives Rejected explains why we didn't choose other options
- References points to implementation files and related decisions

### 2. ADR-005 Multi-Topic Structure
**Decision:** Cover 4 related frontend patterns in single ADR instead of creating 4 separate ADRs.

**Rationale:** Topics are interconnected:
- Server/Client split affects where to use hooks
- URL state management requires Client Components
- Component composition relates to hook extraction
- All part of cohesive "frontend architecture" story

Single ADR avoids duplication while providing comprehensive frontend guidance.

### 3. Concrete Code Examples
**Decision:** Include actual code snippets from codebase in both ADRs.

**Rationale:** Makes ADRs practical reference documentation, not abstract principles. Developers can:
- See pattern in action
- Copy/paste template for new features
- Understand context where pattern applies

Examples show:
- ADR-004: Pydantic validator, SQLAlchemy column definition, frontend datetime-local conversion
- ADR-005: Server Component (page.tsx), Client Component (log-list.tsx), custom hooks

### 4. Cross-Referencing Between ADRs
**Decision:** ADR-005 references ADR-001 for detailed URL state management rationale instead of duplicating content.

**Rationale:** DRY principle for documentation. ADR-001 already covers:
- Root cause of filter reactivity bug
- Comparison of 4 alternative approaches
- Migration path from prop-based to URL-based state

ADR-005 documents the architectural principle, ADR-001 documents the discovery and solution.

## Performance Impact

**Documentation quality:** Two comprehensive ADRs demonstrate technical depth across backend and frontend architecture.

**Requirements coverage:** DOC-03 fully addressed (5 ADRs total covering major architectural decisions).

**Maintainability:** New developers can read ADRs to understand:
- Why timestamptz instead of naive timestamps (timezone correctness)
- Why Server/Client hybrid instead of full SPA (SSR performance)
- When to extract custom hooks (reuse criteria)
- Why URL state instead of Context (shareable links)

## Testing

**Validation performed:**
1. File existence check: Both ADR-004 and ADR-005 created in `docs/decisions/`
2. Minimum length check: ADR-004 (433 lines) > 200 lines, ADR-005 (802 lines) > 250 lines
3. Section structure: Both ADRs have all 7 required sections
4. Requirement mapping: ADR-004 mentions DB-02, ANALYTICS-07; ADR-005 mentions UI-05, UI-06
5. Key concepts: ADR-004 mentions timestamptz and UTC; ADR-005 mentions Server Components, hooks, URL state
6. Cross-references: ADR-005 references ADR-001

**All verification checks passed.**

## Integration Points

**With existing ADRs:**
- ADR-005 references ADR-001 for URL state management details
- ADR-004 complements ADR-003 (indexing strategy applies to timestamptz column)

**With requirements:**
- ADR-004 maps to DB-02, ANALYTICS-07, NFR-Correctness, API-07
- ADR-005 maps to UI-05, UI-06, FILTER-07, NFR-Maintainability, NFR-Performance

**With implementation:**
- ADR-004 references `backend/app/models.py`, `backend/app/schemas/logs.py`, `backend/app/routers/analytics.py`
- ADR-005 references `frontend/src/app/logs/page.tsx`, `frontend/src/hooks/use-log-filters.ts`, `frontend/src/hooks/use-infinite-scroll.ts`

## Lessons Learned

### What Went Well
1. **Extended ADR template works:** 7-section structure provides comprehensive coverage while maintaining readability.

2. **Concrete examples valuable:** Code snippets from actual codebase make ADRs practical reference material, not abstract theory.

3. **Multi-topic ADR effective:** Covering 4 related frontend patterns in ADR-005 created cohesive architectural narrative without duplication.

4. **Cross-referencing avoids duplication:** ADR-005 → ADR-001 reference maintains DRY principle for documentation.

5. **Requirements mapping crucial:** Explicit mapping to DB-02, ANALYTICS-07, UI-05, etc. enables traceability from requirements to decisions to implementation.

### What Could Be Improved
1. **ADR discovery:** Currently no index of ADRs. Consider creating `docs/decisions/README.md` with ADR catalog and decision log.

2. **Status tracking:** ADRs have "Status: Accepted" but no mechanism for "Deprecated" or "Superseded by ADR-XXX" when patterns evolve.

3. **Template consistency:** While structure is consistent, tone varies slightly (ADR-004 more technical, ADR-005 more tutorial-like). Could standardize voice.

### Recommendations for Next Plans
1. **Create ADR index:** Add `docs/decisions/README.md` listing all ADRs with one-line summaries and status.

2. **Add decision log:** Chronological log of when each ADR was created and why.

3. **Consider lightweight ADRs:** Not every decision needs 400+ lines. Could create "ADR-lite" template for smaller decisions (100-200 lines).

## Commits

| Task | Commit | Message | Files |
|------|--------|---------|-------|
| 1 | a9bc0ad | docs(07-02): create ADR-004 for timezone handling | docs/decisions/004-timezone-handling.md |
| 2 | 475a521 | docs(07-02): create ADR-005 for frontend architecture patterns | docs/decisions/005-frontend-architecture.md |

## Summary Statistics

- **Tasks completed:** 2/2 (100%)
- **Files created:** 2
- **Files modified:** 0
- **Total lines written:** 1,235 lines (433 + 802)
- **Commits:** 2
- **Duration:** 596 seconds (~10 minutes)
- **Total ADRs:** 5 (001-005)

## Verification

**Self-check performed:**

```bash
# Check ADR-004 exists
✓ File exists: docs/decisions/004-timezone-handling.md
✓ Minimum length: 433 lines (required: 200)
✓ All 7 required sections present
✓ Requirement mapping present (DB-02, ANALYTICS-07)
✓ Key concepts mentioned (timestamptz, UTC)

# Check ADR-005 exists
✓ File exists: docs/decisions/005-frontend-architecture.md
✓ Minimum length: 802 lines (required: 250)
✓ All required sections present
✓ Requirement mapping present (UI-05, UI-06)
✓ Topics covered (Server Components, Custom Hooks, URL State)
✓ Cross-reference to ADR-001 present

# Check commits exist
✓ Commit a9bc0ad exists (Task 1: ADR-004)
✓ Commit 475a521 exists (Task 2: ADR-005)
```

## Self-Check: PASSED

All files created, all commits exist, all verification checks passed.

---

**Plan Status:** ✅ Complete
**Requirements:** DOC-03 fully addressed (5 ADRs total)
**Next Step:** Update STATE.md, ROADMAP.md, REQUIREMENTS.md, commit metadata
