---
phase: 05
slug: analytics-dashboard
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-23
---

# Phase 05 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (backend) + Jest 29.x (frontend) |
| **Config file** | backend/pyproject.toml + frontend/jest.config.js |
| **Quick run command** | `docker compose exec backend pytest -xvs` |
| **Full suite command** | `docker compose exec backend pytest && cd frontend && npm test -- --run` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `docker compose exec backend pytest -xvs`
- **After every plan wave:** Run full suite (backend + frontend)
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*To be filled by planner based on specific tasks created*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No Wave 0 needed:
- ✅ Backend: pytest + fixtures from Phase 1
- ✅ Frontend: Jest + React Testing Library from Phase 3
- ✅ Recharts tests: can use existing test patterns

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Chart visual rendering | ANALYTICS-03, ANALYTICS-04 | Chart appearance, colors, layout | 1. Navigate to /analytics 2. Verify time-series area chart renders 3. Verify severity bar chart renders with vibrant colors 4. Check responsive layout on mobile |
| Dashboard load performance | Success Criterion #8 | End-to-end timing with 100k logs | 1. Seed 100k logs 2. Navigate to /analytics with 30-day range 3. Measure time from click to charts rendered 4. Must be <2 seconds |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
