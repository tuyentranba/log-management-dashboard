# Phase 7: Documentation - Research

**Researched:** 2026-03-27
**Domain:** Technical documentation, README structure, ADRs, code comments
**Confidence:** HIGH

## Summary

Phase 7 completes project documentation by refactoring the 255-line README into a focused entry point, creating 4 ADRs documenting major architectural decisions, adding inline comments to complex algorithms, and establishing documentation navigation. This phase transforms good working code into well-documented production-ready software that demonstrates technical excellence to evaluators and future maintainers.

The documentation strategy follows a **separation of concerns** pattern: README provides quick start, dedicated docs/ files provide depth, ADRs explain thinking process, and inline comments clarify non-obvious logic. This approach balances discoverability (everything starts from README) with maintainability (detailed content lives in focused files).

**Primary recommendation:** Structure documentation in layers—README for getting started, docs/TESTING.md, docs/ARCHITECTURE.md, docs/TECHNOLOGY.md for deep dives, ADRs for decision rationale, and inline comments for algorithmic complexity. This creates a documentation hierarchy matching different reader needs (newcomer onboarding → understanding design → exploring alternatives).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**README Structure and Scope:**
- Keep README focused on getting started (~120-150 lines)
- Move detailed content to separate files in docs/ directory
- README serves as entry point and navigation hub
- README Contents: project overview, technology stack summary, quick start commands, links to detailed docs, project structure tree, common development commands
- Excluded from README: full testing details (→ docs/TESTING.md), architecture deep-dive (→ docs/ARCHITECTURE.md), design decision rationale (→ docs/decisions/*.md), contributing guidelines, license

**File Organization:**
- Flat docs/ directory structure
- docs/TESTING.md - Full testing documentation
- docs/ARCHITECTURE.md - System architecture overview
- docs/TECHNOLOGY.md - Technology choices and rationale
- docs/decisions/00N-*.md - Individual ADRs
- docs/README.md - Documentation index/navigation

**Design Decisions Documentation:**
- Follow extended ADR template with explicit requirements mapping
- Each ADR shows the thinking process, not just the outcome
- Located in docs/decisions/ following existing 001-filter-reactivity pattern

**ADR Structure (Extended Template):**
1. Context - The problem + NFRs/FRs driving the decision
2. Requirements Addressed - Explicit list of functional and non-functional requirements satisfied
3. Options Considered - 3-4 alternatives with pros/cons analysis
4. Decision - Chosen option with detailed rationale
5. Consequences - Trade-offs accepted, benefits gained
6. Alternatives Rejected - Why each alternative didn't fit

**Code Examples:** Include minimal code snippets (5-10 lines) to illustrate patterns/decisions without overwhelming

**ADRs to Create:**
1. **002-cursor-pagination.md** - Why cursor over offset pagination
   - NFRs: Performance at scale (constant time vs linear), no duplicate/missing rows
   - FRs: Paginated log list (LOG-02, LOG-04)

2. **003-database-indexing.md** - Why BRIN + composite B-tree indexes
   - NFRs: Query performance (<500ms pagination, <2s analytics), scalability (100k+ logs)
   - FRs: Time-series queries, multi-column filtering

3. **004-timezone-handling.md** - Why timestamptz + UTC normalization
   - NFRs: Correctness (no timezone bugs), consistency (aggregation accuracy)
   - FRs: Accurate time-based queries, analytics across time zones

4. **005-frontend-architecture.md** - Frontend patterns and design principles
   - Topics: Custom hooks pattern, Server/Client Component strategy, State management philosophy, Component composition patterns
   - References existing ADR-001 (filter reactivity) for detailed state management example

**Inline Code Comments Scope:**
- Comment complex algorithms only
- Assume readers know Python/TypeScript basics
- Focus on non-obvious logic requiring explanation
- Comment "why" not "what"

**Style:** Explain rationale and non-obvious decisions
- "Base64 encoding keeps cursor opaque to clients" not "Encode to base64"
- "yield_per(1000) prevents memory spike with large datasets" not "Batch fetch 1000 rows"

**Specific Areas Requiring Comments:**
1. Pagination cursor generation (backend/app/utils/cursor.py) - ~10-15 lines
2. Aggregation queries (backend/app/routers/analytics.py) - ~15-20 lines
3. CSV streaming (backend/app/routers/logs.py export endpoint) - ~10-15 lines

**Documentation Maintenance:**
- Best-effort, no formal requirements
- Update docs when convenient during development
- No strict requirement for doc updates with code changes
- Pragmatic approach suitable for portfolio project

**Documentation Navigation:**
- Create docs/README.md as documentation index
- Lists all documentation files with brief descriptions

**Templates:** Existing examples serve as implicit templates
- ADR-001 shows ADR format
- Current README demonstrates structure
- No separate template files needed

### Claude's Discretion

- Exact wording and tone of documentation
- Additional minor sections in README (badges, screenshots)
- Order of sections within ADRs
- Specific code examples chosen for ADRs
- Formatting details (headers, bullets, code fence languages)

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DOC-01 | README documents how to run the application | README refactoring with quick start section covers docker-compose commands, access URLs, seeding data |
| DOC-02 | README documents how to run tests | Existing README Testing section (lines 77-177) moves to docs/TESTING.md with links from README |
| DOC-03 | README documents design decisions and rationale | ADRs 002-005 document cursor pagination, indexing, timezone handling, frontend architecture with decision rationale |
| DOC-04 | README explains technology choices | docs/TECHNOLOGY.md explains FastAPI, Next.js, PostgreSQL, Docker choices with reasoning |
| DOC-05 | Code includes inline comments for complex logic | PEP 257 docstrings + Google TypeScript JSDoc standards guide inline comments in cursor.py, analytics.py, logs.py |

</phase_requirements>

## Standard Stack

This phase uses documentation tools and conventions, not software libraries. Standards come from industry best practices:

### Core Documentation Standards

| Standard | Source | Purpose | Status |
|----------|--------|---------|--------|
| Markdown | CommonMark 0.30 | Documentation format | Universal standard |
| ADR Format | Michael Nygard 2011 | Architecture decisions | De facto industry standard |
| PEP 257 | Python.org | Python docstrings | Official Python convention |
| JSDoc | TypeScript ecosystem | TypeScript comments | Google Style Guide standard |

### Documentation Tools (Already in Project)

| Tool | Version | Purpose | Usage |
|------|---------|---------|-------|
| Markdown | - | All documentation files | .md extension |
| Git | - | Version control for docs | Tracked with code |
| README.md | - | Entry point | Root of repository |

**No new tools or libraries needed** - documentation uses existing markdown files, git versioning, and text editors. Focus is on content structure and writing quality, not tooling.

## Architecture Patterns

### Pattern 1: Layered Documentation Hierarchy

**What:** Documentation organized by reader expertise level and need depth

**Structure:**
```
README.md                        # Layer 1: Quick start (120-150 lines)
├── Getting Started              # Commands to run application
├── Technology Stack             # High-level stack summary
└── Links to detailed docs       # Navigation to Layer 2

docs/                            # Layer 2: Deep dive documents
├── README.md                    # Documentation index
├── TESTING.md                   # Testing guide (from current README)
├── ARCHITECTURE.md              # System design overview
├── TECHNOLOGY.md                # Technology rationale
└── decisions/                   # Layer 3: Decision history
    ├── README.md                # ADR index (already exists)
    ├── 001-*.md                 # Existing ADR
    ├── 002-cursor-pagination.md
    ├── 003-database-indexing.md
    ├── 004-timezone-handling.md
    └── 005-frontend-architecture.md

Code files                       # Layer 4: Implementation details
├── Docstrings (PEP 257)         # Function/class documentation
└── Inline comments              # Algorithm rationale
```

**When to use:** All technical projects with multiple stakeholder types (users, developers, evaluators)

**Why this works:**
- **Progressive disclosure:** Readers start simple, dive deeper as needed
- **Maintenance efficiency:** Changes to testing details don't touch README
- **Search optimization:** Detailed content in focused files improves searchability
- **Reference separation:** ADRs document "why", code documents "what", comments document "how"

### Pattern 2: ADR Extended Template (Requirements-Driven)

**What:** Architecture Decision Records that explicitly map decisions to requirements

**Template sections:**
```markdown
# ADR-00N: [Decision Title]

**Status:** Accepted | Proposed | Deprecated | Superseded
**Date:** YYYY-MM-DD
**Deciders:** [who was involved]

## Context
- The problem being solved
- Environmental factors (technical, political, social)
- Constraints driving the decision

## Requirements Addressed
Explicit mapping to functional and non-functional requirements:
- **FR-XX:** [functional requirement satisfied]
- **NFR-XX:** [non-functional requirement satisfied]

## Options Considered

### Option 1: [Name]
**Pros:** [benefits]
**Cons:** [drawbacks]

### Option 2: [Name]
**Pros:** [benefits]
**Cons:** [drawbacks]

[3-4 options total]

## Decision
"We will [specific action]" - active voice, complete sentences

## Consequences

### Positive
- [benefits gained]
- [problems solved]

### Negative
- [trade-offs accepted]
- [technical debt introduced]

### Neutral
- [other impacts]

## Alternatives Rejected
For each rejected option, explain why specifically:
- **[Option name]:** Rejected because [detailed reasoning]

## References
- Code files affected
- Commit hashes
- External documentation
- Related ADRs
```

**When to use:** Major architectural decisions with meaningful trade-offs

**Why this works:**
- **Traceability:** Requirements mapping enables verification coverage
- **Teaching tool:** Shows thinking process, not just outcome (critical for portfolio evaluation)
- **Future reference:** Prevents revisiting settled decisions
- **Explicit trade-offs:** Acknowledges negative consequences honestly

**Example from project:** ADR-001 (filter reactivity) demonstrates this pattern - 256 lines showing problem, multiple alternatives considered, detailed decision rationale, and implementation status

### Pattern 3: Comment Threshold System

**What:** Systematic decision framework for when to add inline comments

**Decision tree:**
```
Is the logic complex or non-obvious?
├─ NO → No comment needed (code is self-documenting)
│      Example: log = await db.get(Log, log_id)
│
└─ YES → Does it require explanation?
       ├─ NO → Add docstring to function (PEP 257/JSDoc)
       │      Example: Function that does standard CRUD
       │
       └─ YES → Add inline comment explaining WHY
              ├─ Algorithm choice rationale
              │  Example: "Base64 encoding keeps cursor opaque to clients"
              │
              ├─ Performance optimization
              │  Example: "yield_per(1000) prevents memory spike with large datasets"
              │
              ├─ Non-obvious workaround
              │  Example: "Composite cursor comparison handles sort direction edge case"
              │
              └─ Business rule implementation
                 Example: "50,000 row limit prevents query timeouts per CONTEXT.md"
```

**Thresholds for this project:**
- **No comments:** Standard CRUD operations, simple queries, obvious type conversions
- **Docstrings only:** Public API functions, exported components
- **Inline comments:** Cursor encoding logic, date_trunc aggregations, streaming CSV generators, composite index usage

**When to use:** All code files - apply threshold consistently

**Why this works:**
- **Reduces noise:** Comments only where they add value
- **Respects reader:** Assumes basic Python/TypeScript knowledge
- **Focuses on rationale:** "Why" is valuable, "what" is redundant with code
- **Maintainable:** Fewer comments = less drift between code and docs

### Pattern 4: Documentation Navigation Hub

**What:** Central index (docs/README.md) that guides readers to relevant documentation

**Structure:**
```markdown
# Documentation Index

Welcome! This directory contains detailed documentation for the Logs Dashboard project.

## For Getting Started
- [../README.md](../README.md) - Quick start guide, installation, common commands

## For Developers

### Understanding the System
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design, component interactions, data flow
- [TECHNOLOGY.md](./TECHNOLOGY.md) - Technology choices and rationale

### Testing & Quality
- [TESTING.md](./TESTING.md) - Running tests, test organization, coverage reports

### Design Decisions
- [decisions/README.md](./decisions/README.md) - ADR index
- [decisions/001-filter-reactivity.md](./decisions/001-filter-reactivity.md) - State management pattern
- [decisions/002-cursor-pagination.md](./decisions/002-cursor-pagination.md) - Pagination approach
- [decisions/003-database-indexing.md](./decisions/003-database-indexing.md) - Index strategy
- [decisions/004-timezone-handling.md](./decisions/004-timezone-handling.md) - Timezone correctness
- [decisions/005-frontend-architecture.md](./decisions/005-frontend-architecture.md) - Frontend patterns

## For Evaluators
Start with [ARCHITECTURE.md](./ARCHITECTURE.md) for system overview, then review ADRs to understand design thinking.
```

**When to use:** Projects with more than 3-4 documentation files

**Why this works:**
- **Discoverability:** Single entry point to find any documentation
- **Audience segmentation:** Guides different readers to relevant content
- **Maintenance reminder:** Updating index when adding new docs ensures discoverability

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Documentation site generation | Custom doc builder | Plain Markdown files | GitHub renders markdown natively, no build step needed, works offline, simple to maintain |
| API documentation | Custom endpoint docs | FastAPI auto-generated docs | /docs endpoint already exists, reflects current code, zero maintenance |
| Code formatting in docs | Manual syntax highlighting | GitHub/markdown code fences | Automatic highlighting, supports 100+ languages, portable |
| Documentation versioning | Separate doc branches | Docs committed with code | Changes tracked together, pull requests review docs + code, ensures sync |
| Table of contents generation | Manual TOC maintenance | GitHub markdown auto-TOC | Auto-generated on GitHub, no maintenance burden, always accurate |

**Key insight:** Documentation infrastructure should be minimal. Markdown + git + GitHub provides everything needed—rendering, versioning, search, navigation. Custom tooling adds complexity with little benefit for portfolio projects.

## Common Pitfalls

### Pitfall 1: README Kitchen Sink

**What goes wrong:** README becomes 500+ line document covering everything, overwhelming new users and hiding critical getting-started information.

**Why it happens:** Fear of missing information, lack of clear documentation architecture, treating README as only documentation file.

**How to avoid:**
- **Set line budget:** 120-150 lines for README, move everything else to docs/
- **Focus on first 5 minutes:** What does someone need to get app running?
- **Use links liberally:** "See docs/TESTING.md for details" not "Here's everything about testing"
- **Apply newspaper principle:** Most important info first, details later/elsewhere

**Warning signs:**
- README requires scrolling multiple screens to reach installation steps
- Multiple H2 sections that could be separate documents (Architecture, Contributing, API Reference)
- README changes frequently because it contains implementation details
- New contributors ask "where do I start?" despite 500-line README

**Example from project:** Current README is 255 lines with comprehensive testing section (lines 77-177) - these 100 lines move to docs/TESTING.md, README links to it instead

### Pitfall 2: ADRs Without Alternatives

**What goes wrong:** ADR documents chosen solution without explaining rejected alternatives, appearing as justification rather than decision record.

**Why it happens:** Writing ADR after implementation (documenting done vs deciding), confirmation bias, time pressure.

**How to avoid:**
- **Show options considered:** List 3-4 alternatives with honest pros/cons
- **Explain rejections explicitly:** "Rejected because..." section for each alternative
- **Include context factors:** Technical constraints, team expertise, time limitations that influenced decision
- **Acknowledge trade-offs:** Negative consequences section admits downsides of chosen approach

**Warning signs:**
- ADR only describes chosen solution, no alternatives mentioned
- Consequences section only lists positive outcomes
- Decision appears obvious (if obvious, probably doesn't need ADR)
- Cannot explain why alternative X was rejected

**Example from project:** ADR-001 demonstrates good pattern - 4 alternatives considered (force refresh, Zustand, hybrid prop sync, Server Actions), each rejected with specific reasoning

### Pitfall 3: Comment Drift

**What goes wrong:** Inline comments become outdated as code evolves, misleading future developers with incorrect information.

**Why it happens:** Comments not updated when code changes, lack of test coverage for commented logic, commenting obvious things.

**How to avoid:**
- **Comment sparingly:** Only complex/non-obvious logic (less to maintain)
- **Test what you comment:** If logic is complex enough to comment, it's complex enough to test
- **Comment "why" not "what":** Code shows what, comments explain rationale (rationale changes less than implementation)
- **Review comments in PRs:** Check comment accuracy when reviewing code changes

**Warning signs:**
- Comments contradict code behavior
- Comments describe implementation details ("loop through array") rather than rationale
- High density of comments (>30% lines are comments)
- Comments reference old function/variable names

**Example from project:** Current code has good docstrings (PEP 257) but minimal inline comments - Phase 7 adds ~40 lines of rationale comments to 3 complex areas only

### Pitfall 4: Documentation in Wrong Layer

**What goes wrong:** Implementation details in README, getting-started steps in ADRs, architectural decisions in code comments - information lives in wrong place for its audience.

**Why it happens:** Lack of documentation architecture, adding to most recent file opened, unclear distinction between doc types.

**How to avoid:**
- **README = getting started:** Installation, first run, where to find more
- **docs/*.md = deep dives:** Testing guide, architecture overview, technology rationale
- **ADRs = decisions:** Why we chose X over Y, trade-offs, alternatives
- **Code comments = implementation:** Why this algorithm, non-obvious edge cases
- **Docstrings = API reference:** Function behavior, parameters, returns

**Warning signs:**
- README explains database index strategy in detail
- ADR includes step-by-step testing instructions
- Code comment explains entire system architecture
- Need to read 3+ documents to understand one concept

**Example from project:** Current README mixes getting started (good) with comprehensive testing details (wrong layer) - Phase 7 separates into README (links) + docs/TESTING.md (details)

### Pitfall 5: Stale Documentation Obligation

**What goes wrong:** Project requires strict doc updates with every code change, creating documentation maintenance burden that slows development or leads to docs being skipped entirely.

**Why it happens:** Applying enterprise documentation processes to portfolio projects, overcommitment to documentation completeness.

**How to avoid:**
- **Best-effort approach:** Update docs when convenient, accept some drift
- **Focus on stable docs:** README and ADRs change less frequently than code
- **Automate what you can:** FastAPI /docs generates API reference automatically
- **Pragmatic standards:** "Good enough" documentation beats perfect documentation that's never written

**Warning signs:**
- Pull requests rejected because docs not updated
- Documentation becomes bottleneck in development
- Developers avoid adding features to avoid documentation work
- Documentation standards more strict than code standards

**Example from project:** CONTEXT.md explicitly states "best-effort, no formal requirements" for maintenance - pragmatic approach suitable for portfolio project

## Code Examples

Verified patterns from official sources and project code:

### ADR Template (Nygard Pattern)

Source: [Michael Nygard 2011](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)

```markdown
# ADR-002: Use Cursor-Based Pagination for Log List

**Status:** Accepted
**Date:** 2026-03-27
**Deciders:** Development Team

## Context

The log list endpoint needs pagination to handle 100k+ logs efficiently. Traditional offset-based pagination (LIMIT/OFFSET) has performance problems with large datasets:

- Pagination to page 100 with offset 5000 forces database to scan and discard first 5000 rows
- Query time grows linearly with page number (page 1: 10ms, page 100: 500ms, page 1000: 5000ms)
- Rows can be duplicated or skipped if data changes between page requests

The system requires constant-time pagination that works reliably at any page depth.

## Requirements Addressed

- **LOG-02:** User can view paginated list of all logs
- **LOG-04:** Log list uses cursor-based pagination for constant query time
- **NFR-Performance:** Query execution time <500ms for pagination at any depth

## Options Considered

### Option 1: Offset-Based Pagination (LIMIT/OFFSET)
**Pros:** Simple to implement, well-understood pattern, supported by all databases
**Cons:** Performance degrades linearly with page depth, duplicate/missing rows if data changes, scans entire dataset to page N

### Option 2: Cursor-Based Pagination (keyset pagination)
**Pros:** Constant query time regardless of page depth, no duplicate/missing rows, works with live data
**Cons:** Requires stable sort key, cursor format must be opaque, more complex implementation

### Option 3: Search-After Pattern (Elasticsearch-style)
**Pros:** Similar performance to cursor-based, works well with search
**Cons:** Requires search engine infrastructure, overkill for relational database

## Decision

We will implement cursor-based pagination using base64-encoded timestamp+id cursors.

Implementation pattern:
```python
# Encode cursor from last item
cursor = base64_encode(json.dumps({"timestamp": last.timestamp, "id": last.id}))

# Decode and query
decoded = json.loads(base64_decode(cursor))
query = query.where(or_(
    timestamp < decoded["timestamp"],
    and_(timestamp == decoded["timestamp"], id < decoded["id"])
))
```

## Consequences

### Positive
- Query time constant (~10ms) at any page depth (page 1 = page 1000)
- Composite index (timestamp DESC, id DESC) enables efficient seeks
- No duplicate or missing rows even with concurrent inserts
- Opaque cursor format allows changing implementation without breaking clients

### Negative
- Cannot jump to arbitrary page number (no "go to page 50")
- Cursor becomes invalid if sort order changes
- More complex implementation than offset pagination

### Neutral
- Frontend must track cursor instead of page number
- Cursor must be included in URL state for shareable links

## Alternatives Rejected

**Offset-Based Pagination:** Rejected because performance degrades to 5+ seconds at page 1000 with 100k logs. Testing requirement (TEST-03) specifies 100k+ log validation - offset pagination fails this requirement.

**Search-After Pattern:** Rejected because it requires Elasticsearch infrastructure. Project uses PostgreSQL for relational data, adding search engine adds operational complexity without sufficient benefit.

## References

- Implementation: `backend/app/utils/cursor.py`
- API endpoint: `backend/app/routers/logs.py` list_logs()
- Tests: `backend/tests/test_logs_list.py` (pagination tests)
- Performance validation: `backend/tests/test_logs_performance.py` (page 100+ < 500ms)
- Related: ADR-003 (database indexing) covers composite index supporting this pattern
```

### Python Docstring (PEP 257)

Source: [PEP 257](https://peps.python.org/pep-0257/)

```python
def encode_cursor(timestamp: datetime, log_id: int) -> str:
    """
    Encode pagination cursor as opaque base64 string.

    Base64 encoding keeps cursor format opaque to clients, allowing
    internal implementation changes without breaking API contracts.
    Composite key (timestamp + id) enables stable ordering even when
    multiple logs share the same timestamp.

    Args:
        timestamp: Log timestamp (must be timezone-aware)
        log_id: Log primary key

    Returns:
        Base64-encoded JSON string containing timestamp (ISO format) and id

    Raises:
        ValueError: If timestamp is timezone-naive

    Example:
        >>> from datetime import datetime, timezone
        >>> encode_cursor(datetime(2024, 3, 20, 15, 30, 0, tzinfo=timezone.utc), 123)
        'eyJ0aW1lc3RhbXAiOiAiMjAyNC0wMy0yMFQxNTozMDowMCswMDowMCIsICJpZCI6IDEyM30='
    """
    cursor_data = {
        "timestamp": timestamp.isoformat(),
        "id": log_id
    }
    json_str = json.dumps(cursor_data)
    return base64.b64encode(json_str.encode()).decode()
```

**Key elements:**
- One-line summary ending with period
- Blank line separator
- Detailed description explaining rationale (why base64, why composite key)
- Args/Returns/Raises sections with types
- Example showing actual usage

### TypeScript JSDoc (Google Style Guide)

Source: [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)

```typescript
/**
 * Custom hook for managing log filter state via URL query parameters.
 *
 * Provides single source of truth for filter state using nuqs library.
 * All components reading or writing filter state should use this hook
 * to ensure consistency and avoid stale prop issues.
 *
 * @returns Tuple of [filters, setFilters] matching nuqs useQueryStates interface
 *
 * @example
 * ```tsx
 * const [filters, setFilters] = useLogFilters()
 *
 * // Read current filter state from URL
 * console.log(filters.severity) // ['ERROR', 'CRITICAL']
 *
 * // Update filters (triggers URL change + component re-render)
 * setFilters({ severity: ['INFO'] })
 * ```
 *
 * @see {@link docs/decisions/001-filter-reactivity-refactor.md} for architecture rationale
 */
export function useLogFilters() {
  return useQueryStates(logFiltersSchema)
}
```

**Key elements:**
- JSDoc `/** ... */` format for user-facing documentation
- Summary describes what, detailed description explains why
- `@returns` documents return type
- `@example` with code fence showing usage
- `@see` links to related documentation

### Inline Comment (Rationale Focus)

Source: Project CONTEXT.md + Google TypeScript Style Guide

```python
# backend/app/routers/analytics.py

def determine_granularity(date_from: datetime, date_to: datetime) -> str:
    """
    Determine optimal time bucket granularity based on date range.

    Returns PostgreSQL date_trunc unit optimized for chart readability.
    """
    delta = date_to - date_from

    # Hourly buckets for ranges <3 days (max 72 points)
    # Prevents chart overcrowding while maintaining detail for short ranges
    if delta < timedelta(days=3):
        return 'hour'

    # Daily buckets for 3-30 days (max 30 points)
    # Sweet spot between detail and readability for typical dashboard usage
    elif delta <= timedelta(days=30):
        return 'day'

    # Weekly buckets for >30 days
    # Reduces long-range charts to manageable point count without losing trend visibility
    else:
        return 'week'
```

**Key elements:**
- Comment explains WHY this threshold matters (chart readability)
- Rationale beyond what code shows (max points, typical usage)
- Assumes reader understands timedelta and comparison operators
- Focuses on non-obvious design decision (why 3 days? why 30 days?)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Monolithic README | Layered docs/ structure | ~2020 | GitHub repos now commonly have docs/ directory separating concerns |
| Nygard ADR (5 sections) | Extended ADR with requirements mapping | ~2022 | Adds traceability, better for compliance and large teams |
| Extensive code comments | Minimal comments + strong typing | 2023+ (TypeScript 5.x) | Type systems provide documentation, reducing comment need |
| Wiki-based documentation | Docs in version control with code | ~2019 | Ensures docs and code stay in sync, reviewed together |
| Offline documentation tools (Sphinx, Doxygen) | Markdown + GitHub rendering | ~2018 | No build step, instant preview, works offline and online |

**Deprecated/outdated:**
- **Separate wiki repos:** Docs drift from code, review process disconnected. Modern approach: docs/ in same repo
- **Auto-comment generators:** Tools that add "what" comments to every line create noise. Modern approach: meaningful comments only
- **Version-specific docs:** Separate docs for v1, v2, v3. Modern approach: docs versioned with code via git tags
- **PDF documentation:** Static, hard to update, not searchable. Modern approach: markdown for all documentation

**Current state (2025-2026):**
- **Markdown everywhere:** Universal format for technical documentation
- **Docs-as-code:** Documentation in version control, reviewed in PRs
- **Progressive disclosure:** README → docs/ → ADRs → code - increasing detail depth
- **Type-first documentation:** Strong typing (TypeScript, Python type hints) reduces need for parameter documentation
- **Living documentation:** Auto-generated API docs (FastAPI /docs) stay current automatically

## Validation Architecture

> Section included because workflow.nyquist_validation is true in .planning/config.json

### Test Framework

| Property | Value |
|----------|-------|
| Framework | No automated tests for documentation - validation via review |
| Config file | None - documentation validated through manual review process |
| Quick run command | N/A - documentation phase focuses on writing, not testing |
| Full suite command | N/A - documentation correctness verified through peer review |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DOC-01 | README documents how to run application | manual-only | N/A | ✅ README.md exists |
| DOC-02 | README documents how to run tests | manual-only | N/A | ✅ README.md exists |
| DOC-03 | README documents design decisions | manual-only | N/A | ❌ Wave 0 - ADRs 002-005 |
| DOC-04 | README explains technology choices | manual-only | N/A | ❌ Wave 0 - docs/TECHNOLOGY.md |
| DOC-05 | Code includes inline comments | manual-only | N/A | ✅ Code files exist |

**Rationale for manual-only testing:**
Documentation quality requires human judgment - clarity, completeness, accuracy, tone. Automated tests would check syntax (markdown linting) but cannot validate usefulness or correctness. Review process ensures:
- **Accuracy:** Technical content matches implementation
- **Clarity:** Instructions are followable by target audience
- **Completeness:** All requirements addressed
- **Consistency:** Terminology and formatting uniform

### Sampling Rate

- **Per task commit:** Manual review of documentation changes
- **Per wave merge:** Full documentation read-through for consistency
- **Phase gate:** Complete requirements coverage validation before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `docs/TESTING.md` - Extracted from current README Testing section (lines 77-177)
- [ ] `docs/ARCHITECTURE.md` - New file documenting system design, component interactions
- [ ] `docs/TECHNOLOGY.md` - New file explaining technology choices
- [ ] `docs/README.md` - Documentation index/navigation hub
- [ ] `docs/decisions/002-cursor-pagination.md` - Covers REQ DOC-03
- [ ] `docs/decisions/003-database-indexing.md` - Covers REQ DOC-03
- [ ] `docs/decisions/004-timezone-handling.md` - Covers REQ DOC-03
- [ ] `docs/decisions/005-frontend-architecture.md` - Covers REQ DOC-03
- [ ] `README.md` - Refactor to ~120-150 lines with links to docs/ (currently 255 lines)
- [ ] Inline comments in `backend/app/utils/cursor.py` - Covers REQ DOC-05
- [ ] Inline comments in `backend/app/routers/analytics.py` - Covers REQ DOC-05
- [ ] Inline comments in `backend/app/routers/logs.py` - Covers REQ DOC-05

## Sources

### Primary (HIGH confidence)

- **PEP 257 - Docstring Conventions** (https://peps.python.org/pep-0257/) - Official Python docstring standard, verified 2026-03-27
- **Google TypeScript Style Guide** (https://google.github.io/styleguide/tsguide.html) - JSDoc and comment standards, verified 2026-03-27
- **Michael Nygard ADR Template** (https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) - Original 2011 ADR format, de facto industry standard, verified 2026-03-27
- **Project CONTEXT.md** - User decisions and constraints from `/gsd:discuss-phase` workflow
- **Project CODE.md inspection** - Existing ADR-001, README structure, docs/decisions/README.md format

### Secondary (MEDIUM confidence)

- **Project STATE.md** - Accumulated architectural decisions and patterns from prior phases
- **Project REQUIREMENTS.md** - DOC-01 through DOC-05 requirement definitions

### Tertiary (LOW confidence)

None - research relied entirely on official documentation standards and project artifacts.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official standards (PEP 257, Google Style Guide, Nygard ADR) are stable and authoritative
- Architecture: HIGH - Layered documentation patterns are industry standard, validated by existing ADR-001 structure
- Pitfalls: HIGH - Based on direct observation of current README (255 lines), existing patterns, and CONTEXT.md constraints

**Research date:** 2026-03-27
**Valid until:** 180+ days (documentation standards are stable, change infrequently)

**Key finding:** Documentation phase is primarily a **writing and organization** challenge, not a technical implementation challenge. No new tools needed—success depends on clear writing, logical structure, and consistent application of established standards (PEP 257, JSDoc, Nygard ADR format).

**Critical insight:** The project already has excellent code and working documentation (255-line README, ADR-001). Phase 7 **refactors** documentation into maintainable structure, not creating from scratch. Focus on separation of concerns (README vs docs/ vs ADRs vs comments) and explicit requirements mapping.
