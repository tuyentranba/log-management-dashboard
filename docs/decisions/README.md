# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for the Logs Dashboard project.

## What is an ADR?

An ADR is a document that captures an important architectural decision made along with its context and consequences. It provides:

- **Historical context** - Why we made certain decisions
- **Trade-off analysis** - What we considered and why we chose this path
- **Future reference** - Help future maintainers understand the reasoning

## When to Create an ADR

Create an ADR for decisions that:

- Change the architectural structure (frontend/backend patterns, state management)
- Introduce new infrastructure components (Redis, message queues, caching layers)
- Establish development patterns or conventions
- Make significant refactoring decisions
- Have meaningful trade-offs that should be documented

## ADR Format

Each ADR follows this structure:

```markdown
# ADR-XXX: [Decision Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded by ADR-YYY]
**Date:** YYYY-MM-DD
**Deciders:** [Team members involved]

## Context

What is the issue or problem we're addressing? Include:
- Current situation
- Why this needs a decision
- Any constraints or requirements

## Decision

What did we decide to do? Be specific and concrete.

## Consequences

### Positive
- Benefits of this decision
- What problems it solves
- Improvements it enables

### Negative
- Drawbacks or limitations
- Technical debt introduced
- Ongoing maintenance needs

## Alternatives Considered

What other options did we evaluate and why were they rejected?

1. **Alternative 1**: [Description] - Rejected because [reason]
2. **Alternative 2**: [Description] - Rejected because [reason]

## References

- Links to related issues, PRs, documentation
- External resources that informed the decision
```

## ADR Format (Extended Template)

The project uses an extended ADR template with explicit requirements mapping:

- **Context:** The problem and constraints driving the decision
- **Requirements Addressed:** Explicit mapping to functional and non-functional requirements
- **Options Considered:** 3-4 alternatives with honest pros/cons
- **Decision:** Chosen option with detailed rationale
- **Consequences:** Trade-offs accepted, benefits gained
- **Alternatives Rejected:** Why each alternative didn't fit

## ADR Index

| ID | Status | Date | Decision | Requirements |
|----|--------|------|----------|--------------|
| [ADR-001](./001-filter-reactivity-refactor.md) | Accepted | 2026-03-22 | Client-Side Filter State Management with URL as Source of Truth | FILTER-07 |
| [ADR-002](./002-cursor-pagination.md) | Accepted | 2026-03-20 | Use Cursor-Based Pagination for Log List | LOG-02, LOG-04, NFR-Performance |
| [ADR-003](./003-database-indexing.md) | Accepted | 2026-03-20 | Use BRIN + Composite B-tree Indexes for Time-Series Queries | DB-03, DB-04, DB-05, NFR-Performance |
| [ADR-004](./004-timezone-handling.md) | Accepted | 2026-03-20 | Use timestamptz with UTC Normalization for Timezone Correctness | DB-02, ANALYTICS-07, NFR-Correctness |
| [ADR-005](./005-frontend-architecture.md) | Accepted | 2026-03-21 | Frontend Architecture Patterns and Design Principles | UI-05, UI-06, FILTER-07, NFR-Maintainability |

## Reading Order

**For new developers:**
1. Start with [ADR-005 (Frontend Architecture)](./005-frontend-architecture.md) to understand React patterns
2. Read [ADR-001 (Filter Reactivity)](./001-filter-reactivity-refactor.md) for detailed URL state management
3. Read [ADR-002 (Cursor Pagination)](./002-cursor-pagination.md) to understand pagination approach
4. Read [ADR-003 (Database Indexing)](./003-database-indexing.md) and [ADR-004 (Timezone Handling)](./004-timezone-handling.md) for backend patterns

**For evaluators:**
All ADRs demonstrate decision-making process with alternatives considered and trade-offs explicitly acknowledged.

## Creating a New ADR

1. Copy the template above
2. Number sequentially (next available number)
3. Use kebab-case for filename: `XXX-descriptive-title.md`
4. Update the index table in this README
5. Commit with message: `docs(adr): add ADR-XXX for [decision]`

## ADR Lifecycle

- **Proposed** - Under discussion, not yet implemented
- **Accepted** - Approved and being/been implemented
- **Deprecated** - No longer recommended, but still in use
- **Superseded** - Replaced by a newer decision (link to it)

---

*Last updated: 2026-03-27 (Phase 7 documentation complete)*
