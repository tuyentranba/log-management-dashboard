# Proposed Documentation Structure

## Research: Common Documentation Patterns

### Industry Standards

**1. Divio Documentation System**
- **Tutorials**: Learning-oriented (getting started)
- **How-to guides**: Problem-oriented (recipes)
- **Reference**: Information-oriented (API specs)
- **Explanation**: Understanding-oriented (design decisions)

**2. Microsoft/Google Documentation**
- **Concepts**: High-level explanations
- **Quickstarts**: Fast setup paths
- **Tutorials**: Step-by-step learning
- **Reference**: Complete API/schema docs
- **Samples**: Code examples

**3. Pattern-Oriented (Martin Fowler, Enterprise Patterns)**
- Organize by design patterns and architectural patterns
- Group by concern (persistence, presentation, integration)

**4. Layer-Based (Common in full-stack projects)**
- Frontend patterns
- Backend patterns
- Database patterns
- Infrastructure patterns

## Recommended Structure for Logs Dashboard

```
docs/
├── README.md                          # Navigation hub
│
├── api/
│   ├── README.md                      # API overview
│   ├── contract.md                    # Endpoints, schemas, examples
│   ├── pagination-pattern.md          # Cursor pagination (ADR-002)
│   ├── filtering-pattern.md           # Multi-column filtering
│   └── streaming-pattern.md           # CSV streaming export
│
├── database/
│   ├── README.md                      # Database overview
│   ├── schema.md                      # Table definitions, constraints
│   ├── indexing-pattern.md            # BRIN + B-tree hybrid (ADR-003)
│   ├── queries.md                     # Common query patterns
│   └── migrations.md                  # Alembic migration strategy
│
├── frontend/
│   ├── README.md                      # Frontend overview
│   ├── architecture.md                # SSR/CSR strategy (ADR-005)
│   ├── component-pattern.md           # shadcn/ui component system
│   ├── state-pattern.md               # URL state management (ADR-001)
│   └── styling.md                     # Tailwind patterns
│
├── testing/
│   ├── README.md                      # Testing overview
│   ├── strategy.md                    # Overall testing approach
│   ├── backend-tests.md               # Backend testing guide
│   ├── frontend-tests.md              # Frontend testing guide
│   └── performance-tests.md           # Performance validation
│
├── guides/
│   ├── getting-started.md             # Quick setup
│   ├── development.md                 # Development workflow
│   └── deployment.md                  # Deployment guide
│
└── reference/
    ├── architecture.md                # System architecture overview
    ├── technology.md                  # Tech stack and rationale
    └── glossary.md                    # Terms and definitions
```

## Rationale

### Why Layer-Based Organization?

1. **Intuitive navigation**: Developers naturally think in layers (API, database, frontend)
2. **Pattern proximity**: Related patterns stay together (all API patterns in one place)
3. **Scalability**: Easy to add new patterns without restructuring
4. **Portfolio clarity**: Shows expertise across the full stack

### Why Remove decisions/ Folder?

Current ADRs are essentially **pattern documents**, not traditional "decisions":
- ADR-002 → `api/pagination-pattern.md` (describes cursor pagination pattern)
- ADR-003 → `database/indexing-pattern.md` (describes hybrid indexing pattern)
- ADR-001 → `frontend/state-pattern.md` (describes URL state pattern)
- ADR-005 → `frontend/architecture.md` (describes SSR/CSR strategy)
- ADR-004 → Could be integrated into `database/schema.md` (timezone handling)

**Benefits:**
- Removes artificial "decision" framing (these are patterns, not one-time decisions)
- Groups related content (all database patterns together)
- More scannable for portfolio reviewers
- Still preserves all the valuable "alternatives considered" content

### Migration Mapping

| Current File | New Location | Notes |
|--------------|--------------|-------|
| docs/ARCHITECTURE.md | docs/reference/architecture.md | Reference material |
| docs/TECHNOLOGY.md | docs/reference/technology.md | Reference material |
| docs/TESTING.md | docs/testing/README.md | Testing overview |
| decisions/001-filter-reactivity-refactor.md | docs/frontend/state-pattern.md | Rename to emphasize pattern |
| decisions/002-cursor-pagination.md | docs/api/pagination-pattern.md | API layer concern |
| decisions/003-database-indexing.md | docs/database/indexing-pattern.md | Database layer concern |
| decisions/004-timezone-handling.md | docs/database/schema.md | Integrate into schema doc |
| decisions/005-frontend-architecture.md | docs/frontend/architecture.md | Frontend layer overview |

## Alternative Structures Considered

### Alternative 1: Divio System
```
docs/
├── tutorials/          # Learning-oriented
├── guides/             # Task-oriented
├── reference/          # Information-oriented
└── explanation/        # Understanding-oriented (patterns here)
```
**Rejected**: Too abstract for portfolio project. Reviewers want technical patterns, not pedagogical organization.

### Alternative 2: Flat Structure
```
docs/
├── README.md
├── cursor-pagination-pattern.md
├── hybrid-indexing-pattern.md
├── url-state-pattern.md
├── csv-streaming-pattern.md
└── ...
```
**Rejected**: Doesn't scale. Hard to navigate with many patterns.

### Alternative 3: Keep decisions/ as "patterns/"
```
docs/
├── README.md
├── ARCHITECTURE.md
├── TECHNOLOGY.md
├── TESTING.md
└── patterns/
    ├── cursor-pagination.md
    ├── hybrid-indexing.md
    └── ...
```
**Rejected**: Doesn't group related patterns. All patterns at same level regardless of layer.

## Implementation Plan

### Phase 1: Create New Structure
1. Create new directories: `api/`, `database/`, `frontend/`, `testing/`, `guides/`, `reference/`
2. Create README.md in each directory as navigation index

### Phase 2: Migrate Content
1. Copy ADRs to new locations with new names
2. Update internal links in all documents
3. Migrate top-level docs to `reference/`

### Phase 3: Update Navigation
1. Update root `docs/README.md` with new structure
2. Update root `README.md` to point to new locations
3. Update DIRECTION.md links

### Phase 4: Cleanup
1. Remove `decisions/` directory
2. Verify all links still work
3. Commit with clear migration message

## Open Questions

1. Should we keep "pattern" suffix in filenames? (`pagination-pattern.md` vs `pagination.md`)
   - **Recommendation**: Keep suffix for clarity that these are pattern documents, not API reference

2. Should timezone handling get its own file or integrate into schema.md?
   - **Recommendation**: Integrate into `database/schema.md` with dedicated section

3. Should we split testing guide into multiple files?
   - **Recommendation**: Yes, split into strategy/backend/frontend for better organization

4. Do we need a glossary?
   - **Recommendation**: Optional, can add later if terminology gets complex
