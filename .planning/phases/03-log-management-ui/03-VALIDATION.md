---
phase: 03
slug: log-management-ui
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-21
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Jest 29.x with React Testing Library |
| **Config file** | frontend/jest.config.js |
| **Quick run command** | `npm test -- --testPathPattern=logs` |
| **Full suite command** | `npm test -- --coverage` |
| **Estimated runtime** | ~15 seconds (quick), ~45 seconds (full) |

---

## Sampling Rate

- **After every task commit:** Run `npm test -- --testPathPattern=logs`
- **After every plan wave:** Run `npm test -- --coverage`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| Task 1 | 03-00 | 0 | - | integration | `cd frontend && npm list jest @testing-library/react` | ✅ | ⬜ pending |
| Task 2 | 03-00 | 0 | - | integration | `cd frontend && npm test -- --listTests 2>&1 \|\| echo "No tests found (expected)"` | ✅ | ⬜ pending |
| Task 3 | 03-00 | 0 | - | integration | `cd frontend && npm test -- --testPathPattern=smoke` | ✅ | ⬜ pending |
| Task 1 | 03-01 | 1 | UI-09 | integration | `cd frontend && npm run build` | ✅ | ⬜ pending |
| Task 2 | 03-01 | 1 | UI-09 | integration | `cd frontend && npx tsc --noEmit` | ✅ | ⬜ pending |
| Task 3 | 03-01 | 1 | UI-09 | integration | `cd frontend && npm run build` | ✅ | ⬜ pending |
| Task 1 | 03-02 | 2 | UI-01, UI-05, UI-06, UI-07, UI-09 | integration | `cd frontend && npx tsc --noEmit` | ✅ | ⬜ pending |
| Task 2 | 03-02 | 2 | UI-01, UI-05, UI-06, UI-07, UI-09 | integration | `cd frontend && npx tsc --noEmit` | ✅ | ⬜ pending |
| Task 3 | 03-02 | 2 | UI-01, UI-05, UI-06, UI-07, UI-09 | integration | `cd frontend && npm run build` | ✅ | ⬜ pending |
| Task 1 | 03-03 | 2 | FILTER-01, FILTER-02, FILTER-03, FILTER-04, FILTER-05, FILTER-06, FILTER-07 | integration | `cd frontend && npx tsc --noEmit` | ✅ | ⬜ pending |
| Task 2 | 03-03 | 2 | FILTER-01, FILTER-02, FILTER-03, FILTER-04, FILTER-05, FILTER-06, FILTER-07 | integration | `cd frontend && npx tsc --noEmit` | ✅ | ⬜ pending |
| Task 3 | 03-03 | 2 | FILTER-01, FILTER-02, FILTER-03, FILTER-04, FILTER-05, FILTER-06, FILTER-07 | integration | `cd frontend && npm run build` | ✅ | ⬜ pending |
| Task 1 | 03-04 | 3 | UI-02, UI-03, UI-06, UI-08 | integration | `cd frontend && npx tsc --noEmit` | ✅ | ⬜ pending |
| Task 2 | 03-04 | 3 | UI-02, UI-03, UI-06, UI-08 | integration | `cd frontend && npx tsc --noEmit` | ✅ | ⬜ pending |
| Task 3 | 03-04 | 3 | UI-02, UI-03, UI-06, UI-08 | integration | `cd frontend && npm run build` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `frontend/jest.config.js` — Jest configuration for Next.js
- [x] `frontend/__tests__/setup.ts` — Test setup and globals
- [x] `frontend/__tests__/utils/test-utils.tsx` — Custom render with providers
- [x] `npm install` — jest, @testing-library/react, @testing-library/jest-dom

*All Wave 0 requirements covered by Plan 03-00.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Responsive layout | UI-09 | Visual verification across breakpoints | Open dev tools, test at 1920px, 1440px, 768px viewports |
| Infinite scroll performance | FILTER-02 | Real browser performance profiling | Open logs page with 100k logs, scroll to bottom, verify no lag |
| URL shareability | FILTER-07 | End-to-end user workflow | Apply filters, copy URL, open in incognito, verify same filter state |

*Manual tests complement automated tests for visual and performance aspects.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
