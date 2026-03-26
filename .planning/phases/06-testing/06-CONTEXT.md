# Phase 6: Testing - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Comprehensive test coverage that validates correctness and performance of backend logic, API endpoints, and database queries. Backend achieves 80%+ line coverage with unit and integration tests. Frontend tests cover critical paths (forms, modals, API integration) with 80%+ line coverage. Performance tests verify query execution times meet success criteria (<500ms list, <2s analytics) with 100k logs.

</domain>

<decisions>
## Implementation Decisions

### Coverage Targets and Measurement

**Backend coverage:**
- Target: 80%+ line coverage (matches ROADMAP.md success criteria)
- Tool: pytest-cov for coverage measurement
- Type: Line coverage (not branch coverage)
- Enforcement: Report only - no build failures for coverage drops
- Reports: Terminal summary + HTML report (htmlcov/ directory)

**Frontend coverage:**
- Target: 80%+ line coverage (same standard as backend)
- Tool: Jest built-in coverage (istanbul)
- Type: Line coverage
- Enforcement: Report only - no build failures
- Reports: Terminal summary + HTML report

**Philosophy:**
- Coverage is a visibility metric, not a gate
- Focus on meaningful tests over coverage %
- 80% target demonstrates production-ready quality without over-testing trivial code

### Frontend Test Scope

**What to test:**
- Critical paths only: Forms (CreateForm, EditForm), modals (LogDetailModal, CreateLogModal), filters, API integration
- Skip: Pure presentational components (badges, skeleton loaders, layout wrappers)
- No E2E tests with Playwright/Cypress - unit + integration sufficient for portfolio scope

**API interaction testing:**
- Mock API responses using jest.mock or MSW
- No real API calls in frontend tests - fast, isolated tests
- Mock data defined inline in test files (not shared fixtures)

**Accessibility testing:**
- Include basic a11y checks with jest-axe
- Automated ARIA/semantic HTML validation
- Shows best practices without manual testing overhead

**Test types:**
- Component tests for forms and interactive components
- Integration tests for state management and API calls
- No snapshot tests (too brittle for this project)

### Backend Test Organization

**Structure:**
- Keep current test file organization (test_*.py mirrors modules)
- No service layer extraction - logic stays in routers
- No refactoring to separate unit vs integration directories
- Current approach works well: 111 tests across 2,741 lines

**Mocking strategy:**
- Minimal mocking - real database for integration tests (current approach)
- Function-scoped fixtures ensure test isolation
- No database mocking - tests verify real SQLAlchemy behavior

**Async testing:**
- Continue using pytest-asyncio with asyncio_mode='auto'
- No changes to async testing patterns
- Current setup works well

### Performance Test Strategy

**What to performance test:**
- Pagination queries (expand current test_logs_performance.py)
- Analytics queries (/api/analytics endpoint)
- CSV export with large filtered datasets
- Multi-filter combinations (date + severity + source)

**Performance thresholds:**
- List queries: <500ms with 100k logs (from ROADMAP.md)
- Analytics queries: <2s with 100k logs (from ROADMAP.md)
- Hard thresholds - tests fail if exceeded
- All tests use 100k log dataset (matches seed script)

**Execution:**
- Use @pytest.mark.slow for performance tests
- Can be skipped in quick test runs via `make test-quick`
- Always run in full test suite via `make test`

### Test Data Management

**Backend test data:**
- Function-scoped fixtures (current approach)
- Fresh database per test ensures isolation
- Drop/recreate database between tests (not truncate or rollback)
- Do NOT use seed script for tests - separate small focused datasets

**Frontend test data:**
- Inline mock data in each test file
- No shared mock fixtures or centralized mock library
- Simple, explicit test data

**Database state:**
- Keep current conftest.py pattern: test_engine, test_db, client fixtures
- Separate test_logs_db database (already configured)
- Full isolation between tests - no state leakage

### CI/CD Integration

**Docker setup:**
- Add dedicated test service to docker-compose.yml
- Test service runs pytest and jest
- Separate from dev services (backend, frontend, postgres)
- Uses same test_logs_db database as local tests

**Test database:**
- Keep separate test_logs_db (already configured in conftest.py)
- No shared database with dev environment
- Test DB created/managed by test fixtures

**CI pipeline:**
- No CI setup (GitHub Actions, CircleCI, etc.)
- Portfolio piece - local test execution sufficient
- Avoids CI complexity and setup time

**Makefile commands:**
- Add test targets to existing Makefile
- `make test` - run all tests (backend + frontend)
- `make test-quick` - skip slow tests for fast feedback
- `make coverage` - run tests with coverage reports

### Test Documentation

**Test file documentation:**
- Descriptive test function names only (e.g., `test_create_log_returns_201_with_valid_data`)
- No docstrings on test functions
- Minimal inline comments - only for non-obvious logic

**README Testing section:**
- Add dedicated "Testing" section to README.md (satisfies DOC-02 requirement)
- Document how to run tests (all commands)
- Document coverage requirements (80% target)
- Explain test philosophy (integration over unit, minimal mocking, isolation approach)
- Do NOT document what's covered in detail - keep high-level

**Code comments:**
- Minimal comments in test code
- Only explain non-obvious setup or assertions
- Tests should be self-documenting through clear names

### Test Execution Commands

**Makefile targets to add:**
- `make test` - Run all backend and frontend tests
- `make test-quick` - Run tests excluding @pytest.mark.slow (fast feedback <10s)
- `make coverage` - Run all tests with coverage reports (terminal + HTML)

**Coverage report format:**
- Terminal: pytest-cov prints summary to stdout
- HTML: generates htmlcov/ directory for detailed drill-down
- Both formats generated simultaneously

**No watch mode:**
- Manual test runs only
- No pytest-watch or jest --watch
- Simpler workflow, clearer control

### Claude's Discretion

- Exact test file naming within __tests__/ directory structure
- Specific test helper functions and utilities
- Mock data structure and shape (as long as it matches API types)
- Order of test execution within files
- Exact assertion messages and error text
- HTML coverage report styling/customization

</decisions>

<canonical_refs>
## Canonical References

No external specs - requirements fully captured in decisions above.

Relevant context from project files:
- `.planning/REQUIREMENTS.md` — TEST-01 through TEST-05 define success criteria
- `.planning/ROADMAP.md` Phase 6 — Success criteria for coverage (80%+), performance thresholds (<500ms, <2s), single command execution

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

**Backend test infrastructure (Phase 1):**
- `backend/pyproject.toml` — pytest configuration with asyncio_mode='auto', markers (unit, integration, slow)
- `backend/tests/conftest.py` — Test fixtures: test_engine, test_db, client with function scope
- `backend/tests/test_logs_performance.py` — Existing performance tests for pagination
- 111 test functions already exist covering endpoints, schemas, cursor utilities

**Frontend test infrastructure (Phase 3):**
- `frontend/jest.config.js` — Jest configured for Next.js 15 with automatic transforms
- `frontend/__tests__/utils/test-utils.tsx` — Custom render wrapper with providers
- `frontend/__tests__/smoke.test.tsx` — Smoke test demonstrates infrastructure works
- React Testing Library 16.3.2 installed and configured

**Test database:**
- Separate `test_logs_db` database already configured
- Connection string in conftest.py points to test DB
- Function-scoped fixtures ensure clean slate per test

### Established Patterns

**Backend testing patterns:**
- Integration-heavy approach - tests hit real database
- FastAPI TestClient for HTTP endpoint testing
- Async test support via pytest-asyncio
- Markers for test categorization (unit, integration, slow)

**Frontend testing patterns:**
- Test utilities in __tests__/utils/ directory
- Custom render function with provider wrapper
- Router mocks in global setup file
- Minimal smoke test as foundation

**Docker patterns:**
- docker-compose.yml defines services with health checks
- Makefile provides command shortcuts (make up, make down, make seed)
- Environment variables in .env file

### Integration Points

**Test execution flow:**
1. Docker test service starts postgres and waits for health check
2. Test service runs pytest (backend) and jest (frontend)
3. Coverage reports generated to terminal and HTML
4. Makefile targets provide simple commands

**Coverage integration:**
- pytest-cov generates backend coverage
- Jest built-in coverage generates frontend coverage
- Both write to separate htmlcov directories
- No aggregation needed - separate reports

**Performance test integration:**
- Requires 100k logs in test_logs_db
- Tests can create large dataset in setup or use seed script selectively
- @pytest.mark.slow marker allows skipping in quick runs

</code_context>

<specifics>
## Specific Ideas

- Backend already has strong test foundation (111 tests) - focus on coverage gaps and performance expansion
- Frontend needs significant test additions - currently only smoke test
- Keep pragmatic approach - 80% coverage demonstrates quality without over-testing
- Performance thresholds from ROADMAP.md are clear targets: <500ms list, <2s analytics
- Test execution should be single command (`make test`) for simplicity
- Coverage reports for visibility, not enforcement - portfolio piece shouldn't have flaky gates

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 06-testing*
*Context gathered: 2026-03-27*
