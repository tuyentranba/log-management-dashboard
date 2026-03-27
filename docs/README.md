# Documentation Index

Welcome to the Logs Dashboard documentation! This directory contains detailed technical documentation for understanding, developing, and evaluating the project.

## For Getting Started

- [../README.md](../README.md) - Quick start guide, installation, and common commands

## For Developers

### Understanding the System

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design, component interactions, and data flow
  - Three-tier architecture overview
  - Component interaction diagrams
  - Performance characteristics with 100k logs
  - Database schema and indexing strategy

- [TECHNOLOGY.md](./TECHNOLOGY.md) - Technology choices and rationale
  - Backend stack (FastAPI, PostgreSQL, SQLAlchemy)
  - Frontend stack (Next.js, React, TypeScript, Tailwind)
  - Infrastructure (Docker Compose, Alembic)
  - Alternatives considered and trade-offs accepted

### Testing & Quality

- [TESTING.md](./TESTING.md) - Comprehensive testing guide
  - Running tests (make test, make test-quick, make coverage)
  - Test organization (111 backend tests, frontend component tests)
  - Performance test thresholds (<500ms pagination, <2s analytics)
  - Coverage reports and interpretation
  - Common issues and troubleshooting

### Design Decisions

Architecture Decision Records (ADRs) document major design decisions with explicit requirements mapping and alternatives considered.

- [decisions/README.md](./decisions/README.md) - ADR index
- [decisions/001-filter-reactivity-refactor.md](./decisions/001-filter-reactivity-refactor.md) - URL state management pattern
- [decisions/002-cursor-pagination.md](./decisions/002-cursor-pagination.md) - Why cursor over offset pagination
- [decisions/003-database-indexing.md](./decisions/003-database-indexing.md) - BRIN + composite B-tree strategy
- [decisions/004-timezone-handling.md](./decisions/004-timezone-handling.md) - timestamptz + UTC normalization
- [decisions/005-frontend-architecture.md](./decisions/005-frontend-architecture.md) - Frontend patterns and principles

## For Evaluators

**Start here for portfolio evaluation:**

1. [ARCHITECTURE.md](./ARCHITECTURE.md) - System design overview showing technical thinking
2. [decisions/](./decisions/) - ADRs demonstrating decision-making process with alternatives and trade-offs
3. [TESTING.md](./TESTING.md) - Testing strategy showing production-ready quality

**Key highlights:**
- Cursor-based pagination prevents OFFSET performance degradation ([ADR-002](./decisions/002-cursor-pagination.md))
- BRIN + composite B-tree indexing optimizes time-series queries ([ADR-003](./decisions/003-database-indexing.md))
- timestamptz with UTC normalization prevents timezone bugs ([ADR-004](./decisions/004-timezone-handling.md))
- Server/Client Component strategy balances SSR performance with interactivity ([ADR-005](./decisions/005-frontend-architecture.md))
- 80%+ test coverage with performance validation (<500ms pagination, <2s analytics)

## Documentation Organization

```
docs/
├── README.md                                    # This file - documentation index
├── TESTING.md                                   # Testing guide (~280 lines)
├── ARCHITECTURE.md                              # System design (~340 lines)
├── TECHNOLOGY.md                                # Technology choices (~290 lines)
└── decisions/                                   # Architecture Decision Records
    ├── README.md                                # ADR index
    ├── 001-filter-reactivity-refactor.md        # URL state management (256 lines)
    ├── 002-cursor-pagination.md                 # Pagination approach (~340 lines)
    ├── 003-database-indexing.md                 # Index strategy (~370 lines)
    ├── 004-timezone-handling.md                 # Timezone correctness (~280 lines)
    └── 005-frontend-architecture.md             # Frontend patterns (~300 lines)
```

## Contributing to Documentation

When adding new documentation:

1. **ADRs:** Use extended template with Requirements Addressed section (see existing ADRs for format)
2. **Deep dives:** Add to docs/ directory with clear filename (e.g., DEPLOYMENT.md, MONITORING.md)
3. **Update indices:** Add entry to this README.md and decisions/README.md if applicable
4. **Cross-reference:** Link related docs (ADRs ↔ ARCHITECTURE.md ↔ code comments)

**Best-effort maintenance:** Update docs when convenient, accept some drift. Portfolio project doesn't require enterprise-level doc maintenance.

---

*Last updated: 2026-03-27 (Phase 7 documentation complete)*
