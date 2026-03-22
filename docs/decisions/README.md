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

## ADR Index

| Number | Title | Status | Date |
|--------|-------|--------|------|
| [001](./001-filter-reactivity-refactor.md) | Client-Side Filter State Management | Accepted | 2026-03-22 |

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
