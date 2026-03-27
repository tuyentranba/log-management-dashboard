---
phase: 06
slug: testing
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-27
---

# Phase 06 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 (backend) / jest 29.7.0 (frontend) |
| **Config file** | backend/pyproject.toml / frontend/jest.config.js |
| **Quick run command** | `make test-quick` |
| **Full suite command** | `make test` |
| **Estimated runtime** | ~10 seconds (quick), ~30 seconds (full) |

---

## Sampling Rate

- **After every task commit:** Run `make test-quick`
- **After every plan wave:** Run `make test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 06-00-01 | 00 | 0 | TEST-05 | verify | `grep -q pytest-cov backend/requirements-dev.txt` | ❌ W0 | ⬜ pending |
| 06-00-02 | 00 | 0 | TEST-05 | verify | `grep -q jest-axe frontend/package.json` | ❌ W0 | ⬜ pending |
| 06-00-03 | 00 | 0 | TEST-05 | verify | `grep -q 'test:' Makefile` | ❌ W0 | ⬜ pending |
| 06-01-01 | 01 | 1 | TEST-03 | integration | `pytest backend/tests/test_logs_performance.py -k analytics` | ❌ W0 | ⬜ pending |
| 06-01-02 | 01 | 1 | TEST-03 | integration | `pytest backend/tests/test_logs_performance.py -k export` | ❌ W0 | ⬜ pending |
| 06-01-03 | 01 | 1 | TEST-04 | integration | `pytest backend/tests/test_logs_performance.py -k filtering` | ❌ W0 | ⬜ pending |
| 06-02-01 | 02 | 2 | TEST-01 | unit | `cd frontend && npm test -- create-form.test` | ❌ W0 | ⬜ pending |
| 06-02-02 | 02 | 2 | TEST-01 | unit | `cd frontend && npm test -- edit-form.test` | ❌ W0 | ⬜ pending |
| 06-02-03 | 02 | 2 | TEST-02 | integration | `cd frontend && npm test -- log-detail-modal.test` | ❌ W0 | ⬜ pending |
| 06-02-04 | 02 | 2 | TEST-02 | integration | `cd frontend && npm test -- create-log-modal.test` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/requirements-dev.txt` — add pytest-cov for coverage measurement
- [ ] `frontend/package.json` — add jest-axe for accessibility testing
- [ ] `Makefile` — add test, test-quick, coverage targets
- [ ] `backend/.coveragerc` or `pyproject.toml [tool.coverage.run]` — configure coverage paths
- [ ] `frontend/__tests__/` — create test file stubs for forms and modals

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Coverage reports display correctly | TEST-01 | Visual verification of HTML report | 1. Run `make coverage`<br>2. Open htmlcov/index.html<br>3. Verify 80%+ coverage shown |
| Docker test service runs tests | TEST-05 | Integration with docker-compose | 1. Run `docker-compose up test`<br>2. Verify both backend and frontend tests execute<br>3. Verify exit code 0 on success |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter (pending execution)

**Approval:** pending 2026-03-27
