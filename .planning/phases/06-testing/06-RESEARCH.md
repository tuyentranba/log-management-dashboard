# Phase 6: Testing - Research

**Researched:** 2026-03-27
**Domain:** Python testing (pytest), JavaScript testing (Jest), test coverage tools, performance testing patterns
**Confidence:** HIGH

## Summary

Phase 6 implements comprehensive test coverage validating correctness and performance of all implemented functionality. The project has strong test infrastructure already in place: backend uses pytest 9.0.2 with pytest-asyncio for async testing, and frontend uses Jest 29.7.0 with React Testing Library 16.3.2. Backend currently has 111 tests across ~2,642 lines covering schemas, cursor utilities, health checks, CRUD operations, list/filtering/sorting, CSV export, and analytics. Frontend has only a smoke test. The phase focuses on three areas: (1) expanding backend test coverage to 80%+ with pytest-cov, (2) adding frontend tests for critical paths (forms, modals, API integration) with Jest coverage, and (3) expanding performance tests to verify query execution times (<500ms list, <2s analytics) with 100k+ logs.

**Primary recommendation:** Use pytest-cov for backend coverage measurement (terminal + HTML reports) and Jest built-in coverage for frontend. Keep pragmatic integration-heavy testing approach (real database, minimal mocking). Add Makefile targets for test execution (`make test`, `make test-quick`, `make coverage`). Expand existing test_logs_performance.py to cover analytics queries and CSV export. Add frontend tests for CreateForm, EditForm, LogDetailModal, CreateLogModal, and API integration using jest.mock for API mocking (not MSW - simpler for this scope). Use jest-axe for basic accessibility validation. Coverage targets are 80% line coverage (not branch) for both backend and frontend, enforced via reporting only (no build failures).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Coverage Targets and Measurement:**
- Backend: 80%+ line coverage using pytest-cov (terminal + HTML reports)
- Frontend: 80%+ line coverage using Jest built-in coverage
- Coverage type: Line coverage only (not branch coverage)
- Enforcement: Report only - no build failures for coverage drops
- Philosophy: Coverage is visibility metric, not gate; focus on meaningful tests over coverage %

**Frontend Test Scope:**
- Test critical paths only: Forms (CreateForm, EditForm), modals (LogDetailModal, CreateLogModal), filters, API integration
- Skip pure presentational components (badges, skeleton loaders, layout wrappers)
- No E2E tests (Playwright/Cypress) - unit + integration sufficient for portfolio scope
- Mock API responses using jest.mock (not MSW - inline mock data in test files)
- Include basic accessibility testing with jest-axe
- No snapshot tests (too brittle)

**Backend Test Organization:**
- Keep current test file organization (test_*.py mirrors modules)
- No service layer extraction or refactoring
- No separate unit vs integration directories
- Minimal mocking - real database for integration tests (current approach)
- Function-scoped fixtures ensure test isolation
- Continue using pytest-asyncio with asyncio_mode='auto'

**Performance Test Strategy:**
- Test pagination, analytics, CSV export, multi-filter combinations
- Hard thresholds: List queries <500ms, analytics <2s with 100k logs
- Tests fail if thresholds exceeded
- Use @pytest.mark.slow marker for performance tests
- Can be skipped in quick runs via `make test-quick`
- Always run in full suite via `make test`

**Test Data Management:**
- Backend: Function-scoped fixtures, fresh database per test (drop/recreate, not truncate)
- Do NOT use seed script for tests - separate small focused datasets
- Frontend: Inline mock data in each test file (no shared fixtures)
- Separate test_logs_db database (already configured)

**CI/CD Integration:**
- Add dedicated test service to docker-compose.yml
- No CI setup (GitHub Actions, CircleCI, etc.) - portfolio piece, local execution sufficient
- Makefile commands: `make test`, `make test-quick`, `make coverage`

**Test Documentation:**
- Descriptive test function names only (no docstrings on test functions)
- Minimal inline comments (only for non-obvious logic)
- Add "Testing" section to README.md with: how to run tests, coverage requirements, test philosophy
- Do NOT document what's covered in detail - keep high-level

**Test Execution Commands:**
- `make test` - Run all backend and frontend tests
- `make test-quick` - Run tests excluding @pytest.mark.slow (fast feedback <10s)
- `make coverage` - Run all tests with coverage reports (terminal + HTML)
- No watch mode (pytest-watch or jest --watch)

### Claude's Discretion

- Exact test file naming within __tests__/ directory structure
- Specific test helper functions and utilities
- Mock data structure and shape (as long as it matches API types)
- Order of test execution within files
- Exact assertion messages and error text
- HTML coverage report styling/customization

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TEST-01 | Unit tests cover backend business logic | pytest infrastructure exists, pytest-cov for coverage measurement, existing pattern of unit tests in test_cursor.py and test_schemas.py |
| TEST-02 | Integration tests cover API endpoints | FastAPI TestClient with AsyncClient pattern established, 111 tests already cover endpoints (CRUD, list, export, analytics), need to ensure all endpoints have success/error cases |
| TEST-03 | Tests verify database query performance with 100k+ logs | test_logs_performance.py demonstrates pattern using bulk_insert_mappings, time.perf_counter() for measurement, @pytest.mark.slow marker, need to expand to analytics and CSV export |
| TEST-04 | Tests verify pagination, filtering, and sorting correctness | test_logs_list.py has 25 tests covering these areas, test_logs_performance.py validates pagination consistency, existing patterns can be expanded |
| TEST-05 | Tests runnable via single command | Makefile exists with `make test` target, need to update to run both backend (pytest) and frontend (jest) tests, add coverage and quick targets |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 9.0.2 | Python testing framework | De facto standard for Python testing, async support via pytest-asyncio, powerful fixture system |
| pytest-asyncio | 1.3.0 | Async test support | Required for testing FastAPI async endpoints, auto mode eliminates decorator boilerplate |
| pytest-cov | latest (add) | Coverage measurement | Official pytest plugin wrapping coverage.py, seamless integration with pytest workflow |
| httpx | 0.28.1 (installed) | HTTP client for testing | Async HTTP client for FastAPI TestClient, matches FastAPI's httpx dependency |
| Jest | 29.7.0 (installed) | JavaScript testing framework | Standard for React/Next.js testing, built-in coverage via Istanbul, snapshot support |
| React Testing Library | 16.3.2 (installed) | React component testing | Encourages testing user behavior not implementation, official React team recommendation |
| jest-axe | latest (add) | Accessibility testing | Automated a11y validation in Jest tests, catches ARIA/semantic HTML issues |
| @testing-library/user-event | 14.5.3 (installed) | User interaction simulation | More realistic user interactions than fireEvent, async by default |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| coverage.py | (via pytest-cov) | Coverage engine | Underlying coverage measurement, configured via pytest-cov |
| @testing-library/jest-dom | 6.9.1 (installed) | Custom Jest matchers | Semantic matchers like toBeInTheDocument(), toHaveAttribute() for better assertions |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pytest-cov | coverage.py directly | pytest-cov provides seamless pytest integration, simpler workflow than manual coverage runs |
| jest.mock | MSW (Mock Service Worker) | MSW provides HTTP interception but adds complexity; jest.mock sufficient for this scope |
| Jest | Vitest | Vitest is faster but Jest has mature Next.js integration via next/jest plugin |
| React Testing Library | Enzyme | Enzyme tests implementation details, React Testing Library tests user behavior (better practice) |

**Installation:**

Backend (add to requirements-dev.txt):
```bash
pytest-cov==6.0.0
```

Frontend (add to package.json devDependencies):
```bash
npm install --save-dev jest-axe
```

## Architecture Patterns

### Recommended Project Structure

**Backend tests:**
```
backend/tests/
├── conftest.py              # Shared fixtures (test_engine, test_db, client)
├── test_config.py           # Unit tests for configuration
├── test_schemas.py          # Unit tests for Pydantic schemas
├── test_cursor.py           # Unit tests for cursor utilities
├── test_health.py           # Integration tests for health endpoint
├── test_logs_crud.py        # Integration tests for CRUD operations
├── test_logs_list.py        # Integration tests for list/filter/sort
├── test_export.py           # Integration tests for CSV export
├── test_analytics.py        # Integration tests for analytics
└── test_logs_performance.py # Performance tests (marked @pytest.mark.slow)
```

**Frontend tests:**
```
frontend/__tests__/
├── setup.ts                 # Global test setup (mocks, matchers)
├── utils/
│   └── test-utils.tsx       # Custom render with providers
├── components/
│   ├── create-form.test.tsx # Form validation, submission
│   ├── edit-form.test.tsx   # Form pre-population, update
│   ├── log-detail-modal.test.tsx # Modal rendering, mode toggle
│   └── create-log-modal.test.tsx # Modal open/close, form integration
├── api/
│   └── api-integration.test.tsx # API client functions with mocked responses
└── smoke.test.tsx           # Basic infrastructure validation
```

### Pattern 1: Backend Integration Tests with Real Database

**What:** Tests hit real PostgreSQL database using function-scoped fixtures for complete isolation

**When to use:** All API endpoint tests, any tests requiring database queries

**Example:**
```python
# Source: backend/tests/test_logs_crud.py (existing pattern)
@pytest.mark.asyncio
async def test_create_log_returns_201_with_valid_data(client: AsyncClient):
    """POST /api/logs creates log and returns 201."""
    payload = {
        "timestamp": "2024-01-15T10:30:00Z",
        "message": "Test log entry",
        "severity": "INFO",
        "source": "test-service"
    }

    response = await client.post("/api/logs", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Test log entry"
    assert data["severity"] == "INFO"
```

**Why this pattern:**
- Validates real SQLAlchemy behavior (no ORM mocking)
- Tests actual database constraints and indexes
- Catches timezone/type conversion issues
- Function-scoped fixtures prevent test pollution

### Pattern 2: Performance Tests with Large Datasets

**What:** Tests measure query execution time with 100k+ logs, marked as slow for optional skipping

**When to use:** Pagination, filtering, sorting, analytics, CSV export performance validation

**Example:**
```python
# Source: backend/tests/test_logs_performance.py (existing pattern)
import time
import pytest

pytestmark = pytest.mark.slow  # Mark entire module as slow

@pytest.mark.asyncio
async def test_pagination_performance_deep_page(client: AsyncClient, test_db):
    """Page 100+ loads quickly with cursor pagination."""
    # Create 100k logs using bulk_insert_mappings
    logs = []
    base_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    for i in range(100_000):
        logs.append({
            "timestamp": base_time + timedelta(seconds=i * 25),
            "message": f"Performance test log {i}",
            "severity": "INFO" if i % 2 == 0 else "ERROR",
            "source": f"service-{i % 5}"
        })

    await test_db.run_sync(
        lambda sync_session: sync_session.bulk_insert_mappings(Log, logs)
    )
    await test_db.commit()

    # Navigate to page 100
    cursor = None
    for page in range(100):
        response = await client.get(
            f"/api/logs?limit=50&cursor={cursor}" if cursor else "/api/logs?limit=50"
        )
        cursor = response.json()["next_cursor"]

    # Measure page 100 query time
    start = time.perf_counter()
    response = await client.get(f"/api/logs?limit=50&cursor={cursor}")
    duration_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert duration_ms < 500, f"Page 100 took {duration_ms:.2f}ms (target: <500ms)"
```

**Why this pattern:**
- Realistic dataset size (100k matches seed script)
- Hard thresholds prevent performance regressions
- @pytest.mark.slow allows skipping for quick feedback
- bulk_insert_mappings creates test data efficiently

### Pattern 3: Frontend Form Testing with React Testing Library

**What:** Tests form validation, submission, and error handling from user perspective

**When to use:** CreateForm, EditForm, and any interactive components

**Example:**
```typescript
// Pattern for frontend/__tests__/components/create-form.test.tsx
import { render, screen, waitFor } from '@/utils/test-utils'
import userEvent from '@testing-library/user-event'
import { CreateForm } from '@/app/logs/_components/create-form'
import * as api from '@/lib/api'

// Mock API module
jest.mock('@/lib/api')

describe('CreateForm', () => {
  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    const mockCreateLog = jest.spyOn(api, 'createLog').mockResolvedValue({
      id: 1,
      timestamp: '2024-01-15T10:30:00Z',
      message: 'Test message',
      severity: 'INFO',
      source: 'test-source'
    })

    render(<CreateForm onSuccess={jest.fn()} />)

    // Fill form (find by label - accessibility best practice)
    await user.type(screen.getByLabelText(/message/i), 'Test message')
    await user.selectOptions(screen.getByLabelText(/severity/i), 'INFO')
    await user.type(screen.getByLabelText(/source/i), 'test-source')

    // Submit
    await user.click(screen.getByRole('button', { name: /create/i }))

    // Verify API called
    await waitFor(() => {
      expect(mockCreateLog).toHaveBeenCalledWith({
        message: 'Test message',
        severity: 'INFO',
        source: 'test-source',
        timestamp: expect.any(String)
      })
    })
  })

  it('displays validation error for empty message', async () => {
    const user = userEvent.setup()
    render(<CreateForm onSuccess={jest.fn()} />)

    // Submit without filling required field
    await user.click(screen.getByRole('button', { name: /create/i }))

    // Verify error message appears
    expect(await screen.findByText(/message is required/i)).toBeInTheDocument()
  })
})
```

**Why this pattern:**
- Tests from user perspective (find by label/role, not test IDs)
- Validates both success and error paths
- jest.mock isolates component from API implementation
- userEvent provides realistic interactions (typing, clicking)

### Pattern 4: Accessibility Testing with jest-axe

**What:** Automated ARIA/semantic HTML validation in component tests

**When to use:** All interactive components (forms, modals, buttons)

**Example:**
```typescript
// Pattern for frontend/__tests__/components/log-detail-modal.test.tsx
import { render } from '@/utils/test-utils'
import { axe, toHaveNoViolations } from 'jest-axe'
import { LogDetailModal } from '@/app/logs/_components/log-detail-modal'

expect.extend(toHaveNoViolations)

describe('LogDetailModal accessibility', () => {
  it('has no accessibility violations in view mode', async () => {
    const { container } = render(
      <LogDetailModal
        log={{
          id: 1,
          timestamp: '2024-01-15T10:30:00Z',
          message: 'Test log',
          severity: 'INFO',
          source: 'test-service'
        }}
        isOpen={true}
        onClose={jest.fn()}
      />
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
```

**Why this pattern:**
- Catches missing ARIA labels, invalid roles, contrast issues
- Automated validation without manual testing
- Demonstrates best practices for portfolio piece
- Minimal overhead (one assertion per component test)

### Anti-Patterns to Avoid

- **Testing implementation details:** Don't test component state, internal functions, or React lifecycle methods. Test user-observable behavior only.
- **Mocking the database in backend tests:** Don't mock SQLAlchemy or database calls. Use real test database for integration tests to catch ORM/SQL issues.
- **Shared mutable test data:** Don't reuse test data across tests. Function-scoped fixtures ensure complete isolation.
- **Snapshot testing for UI components:** Don't use Jest snapshots. They're brittle and fail on insignificant changes. Test specific behavior instead.
- **Over-mocking in frontend tests:** Don't mock everything. Only mock external dependencies (API calls, router). Test component logic with real React rendering.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Code coverage measurement | Custom coverage tracking or manual analysis | pytest-cov (backend) + Jest built-in coverage (frontend) | Coverage tools handle complex edge cases: branch coverage, line exclusion, parallel execution, report aggregation |
| Test fixtures and isolation | Manual database setup/teardown in each test | pytest fixtures with function scope | Fixtures handle setup/teardown ordering, dependency injection, automatic cleanup, shared configuration |
| HTTP client for API testing | Manual requests or urllib usage | httpx AsyncClient via FastAPI TestClient | TestClient integrates with FastAPI app, handles ASGI transport, maintains async context, matches production HTTP behavior |
| User interaction simulation | Calling event handlers directly | @testing-library/user-event | user-event simulates realistic browser behavior (focus, hover, keyboard), handles timing/async, more accurate than fireEvent |
| Accessibility testing | Manual WCAG checklist | jest-axe | Automated a11y testing catches 30-50% of issues, validates ARIA roles/labels/semantics, integrates with existing tests |
| Performance measurement | Custom timing with Date.now() | time.perf_counter() (Python) | perf_counter provides high-resolution monotonic clock immune to system time adjustments, accurate for microsecond measurements |

**Key insight:** Testing tools have solved complex edge cases (async cleanup, coverage branch tracking, realistic user events, a11y validation). Custom solutions miss these edge cases and create maintenance burden.

## Common Pitfalls

### Pitfall 1: Async Test Cleanup Not Awaited

**What goes wrong:** Test fixtures don't properly clean up async resources (database connections, HTTP clients), leading to "Task was destroyed but it is pending" warnings or connection pool exhaustion.

**Why it happens:** Python asyncio requires explicit awaiting of cleanup operations. Fixtures must use `async with` or manual `await dispose()` patterns.

**How to avoid:**
- Always use `async with` for async context managers in fixtures
- Explicitly dispose async engines: `await engine.dispose()`
- Set pytest-asyncio to function scope: `asyncio_default_fixture_loop_scope = "function"`

**Warning signs:**
- Warnings about pending tasks in test output
- Database connection pool size growing during test runs
- Tests pass individually but fail when run together

### Pitfall 2: Frontend Tests Fail Due to Missing Router Context

**What goes wrong:** Next.js components using useRouter, useSearchParams, or usePathname crash in tests with "invariant: useRouter called outside of Router context" errors.

**Why it happens:** Jest tests run in Node.js without Next.js router. Components that access routing hooks need mocked router context.

**How to avoid:**
- Mock next/navigation in global setup file (__tests__/setup.ts)
- Provide mock implementations for useRouter, useSearchParams, usePathname
- Use existing test-utils.tsx render wrapper that includes necessary providers

**Warning signs:**
- Tests crash immediately when rendering components
- Error messages mention "invariant" or "Router context"
- Components using Link or router hooks fail

### Pitfall 3: Performance Tests Create Data Inefficiently

**What goes wrong:** Performance tests that create 100k logs one-by-one take 5+ minutes to run, defeating the purpose of fast feedback.

**Why it happens:** Individual INSERT statements create 100k database round-trips. Each ORM add() call is a separate transaction.

**How to avoid:**
- Use bulk_insert_mappings with list of dictionaries (not ORM objects)
- Generate all test data in memory first, then single bulk insert
- Pattern: `await test_db.run_sync(lambda sync_session: sync_session.bulk_insert_mappings(Log, logs))`

**Warning signs:**
- Test setup takes longer than actual test execution
- Database CPU spikes during test runs
- Performance test suite takes >1 minute to run

### Pitfall 4: Coverage Reports Include Generated/Vendor Code

**What goes wrong:** Coverage percentage is artificially low because measurement includes migration files, __pycache__, node_modules, or generated code.

**Why it happens:** Default coverage configuration measures everything unless explicitly excluded.

**How to avoid:**
- Backend: Add `--cov=app` to only measure application code (not tests, migrations, scripts)
- Frontend: collectCoverageFrom patterns already exclude node_modules and .d.ts files
- Exclude migration directories: `omit = ["*/migrations/*", "*/alembic/*"]` in .coveragerc

**Warning signs:**
- Coverage report shows files in tests/ or node_modules/
- Coverage percentage doesn't change after adding tests
- HTML report includes Alembic migration files

### Pitfall 5: Flaky Tests Due to Timestamp Comparison

**What goes wrong:** Tests randomly fail when comparing timestamps because of millisecond differences or timezone conversion issues.

**Why it happens:** datetime.now() includes milliseconds, database truncates to seconds, timezone-naive vs timezone-aware comparison.

**How to avoid:**
- Always use timezone-aware datetimes in tests: `datetime(2024, 1, 1, tzinfo=timezone.utc)`
- Round timestamps to seconds when comparing: `timestamp.replace(microsecond=0)`
- Use ISO 8601 string comparison instead of datetime object comparison

**Warning signs:**
- Tests pass locally but fail in CI
- Tests fail randomly (not consistently)
- Error messages show off-by-milliseconds timestamp differences

### Pitfall 6: Test Coverage for Interactive Components Too Narrow

**What goes wrong:** Tests verify component renders but don't test user interactions, leaving critical bugs undetected (form submission, validation, error handling).

**Why it happens:** Initial tests focus on "does it render" without testing actual user flows.

**How to avoid:**
- Test complete user journeys: render → fill form → submit → verify result
- Test error paths: validation failures, API errors, network failures
- Use userEvent for realistic interactions, not just render assertions

**Warning signs:**
- 80% coverage but bugs still slip through
- Tests don't use userEvent or waitFor
- No tests for loading states, error states, or success states

## Code Examples

Verified patterns from official sources:

### pytest-cov Configuration (pyproject.toml)

```toml
# Source: https://pytest-cov.readthedocs.io/en/latest/config.html
[tool.pytest.ini_options]
addopts = [
    "-v",
    "--cov=app",                    # Measure coverage for app/ directory only
    "--cov-report=term-missing",    # Terminal report showing missing lines
    "--cov-report=html:htmlcov",    # HTML report in htmlcov/ directory
    "--strict-markers",
]

[tool.coverage.run]
omit = [
    "*/tests/*",          # Exclude test files from coverage
    "*/migrations/*",     # Exclude database migrations
    "*/conftest.py",      # Exclude test configuration
]

[tool.coverage.report]
skip_empty = true         # Don't report empty files
precision = 2             # Two decimal places for percentages
```

### Jest Coverage Configuration (jest.config.js)

```javascript
// Source: https://jestjs.io/docs/configuration
const customJestConfig = {
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.tsx',
    '!src/components/ui/**',  // Exclude shadcn/ui components
  ],
  coverageThreshold: {
    global: {
      lines: 80,
      statements: 80,
      // Note: Not enforcing branches or functions for pragmatic coverage
    },
  },
  coverageReporters: [
    'text',              // Terminal summary
    'html',              // HTML report in coverage/ directory
    'lcov',              // LCOV for tooling integration
  ],
}
```

### Makefile Test Commands

```makefile
# Source: Existing Makefile pattern
.PHONY: test test-quick coverage

test:
	@echo "Running all tests (backend + frontend)..."
	docker-compose exec backend pytest tests/ -v
	docker-compose exec frontend npm test -- --passWithNoTests

test-quick:
	@echo "Running quick tests (excluding slow performance tests)..."
	docker-compose exec backend pytest tests/ -v -m "not slow"
	docker-compose exec frontend npm test -- --passWithNoTests

coverage:
	@echo "Running tests with coverage reports..."
	docker-compose exec backend pytest tests/ --cov=app --cov-report=term-missing --cov-report=html:htmlcov
	docker-compose exec frontend npm test -- --coverage --passWithNoTests
	@echo ""
	@echo "Coverage reports generated:"
	@echo "  Backend:  backend/htmlcov/index.html"
	@echo "  Frontend: frontend/coverage/lcov-report/index.html"
```

### Backend Analytics Performance Test

```python
# Pattern for test_logs_performance.py expansion
import pytest
import time
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient

pytestmark = pytest.mark.slow

@pytest.mark.asyncio
async def test_analytics_query_performance_with_100k_logs(client: AsyncClient, test_db):
    """Analytics queries complete under 2 seconds with 100k logs."""
    # Create 100k logs with varied timestamps and severities
    logs = []
    base_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    severities = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']

    for i in range(100_000):
        logs.append({
            "timestamp": base_time + timedelta(hours=i // 100),  # Spread over ~41 days
            "message": f"Log message {i}",
            "severity": severities[i % 4],
            "source": f"service-{i % 5}"
        })

    await test_db.run_sync(
        lambda sync_session: sync_session.bulk_insert_mappings(Log, logs)
    )
    await test_db.commit()

    # Measure analytics query time (30-day window)
    date_from = base_time.isoformat()
    date_to = (base_time + timedelta(days=30)).isoformat()

    start = time.perf_counter()
    response = await client.get(
        f"/api/analytics?date_from={date_from}&date_to={date_to}"
    )
    duration_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "time_series" in data
    assert "severity_distribution" in data

    # Hard threshold: analytics queries must complete under 2 seconds
    assert duration_ms < 2000, f"Analytics query took {duration_ms:.2f}ms (target: <2000ms)"
```

### Frontend Form Test with API Mocking

```typescript
// Pattern for __tests__/components/create-form.test.tsx
import { render, screen, waitFor } from '@/__tests__/utils/test-utils'
import userEvent from '@testing-library/user-event'
import { CreateForm } from '@/app/logs/_components/create-form'
import * as api from '@/lib/api'

jest.mock('@/lib/api')

describe('CreateForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('submits valid form data', async () => {
    const user = userEvent.setup()
    const mockOnSuccess = jest.fn()
    const mockCreateLog = jest.spyOn(api, 'createLog').mockResolvedValue({
      id: 1,
      timestamp: '2024-01-15T10:30:00Z',
      message: 'Test message',
      severity: 'INFO',
      source: 'test-source'
    })

    render(<CreateForm onSuccess={mockOnSuccess} />)

    // Fill form (accessibility-focused queries)
    const messageInput = screen.getByLabelText(/message/i)
    await user.type(messageInput, 'Test message')

    const severitySelect = screen.getByLabelText(/severity/i)
    await user.selectOptions(severitySelect, 'INFO')

    const sourceInput = screen.getByLabelText(/source/i)
    await user.type(sourceInput, 'test-source')

    // Submit
    const submitButton = screen.getByRole('button', { name: /create/i })
    await user.click(submitButton)

    // Verify
    await waitFor(() => {
      expect(mockCreateLog).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Test message',
          severity: 'INFO',
          source: 'test-source',
        })
      )
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })

  it('displays validation errors', async () => {
    const user = userEvent.setup()
    render(<CreateForm onSuccess={jest.fn()} />)

    // Submit without filling required fields
    await user.click(screen.getByRole('button', { name: /create/i }))

    // Verify error messages appear
    expect(await screen.findByText(/message.*required/i)).toBeInTheDocument()
  })

  it('handles API error gracefully', async () => {
    const user = userEvent.setup()
    jest.spyOn(api, 'createLog').mockRejectedValue(new Error('API Error'))

    render(<CreateForm onSuccess={jest.fn()} />)

    // Fill and submit form
    await user.type(screen.getByLabelText(/message/i), 'Test')
    await user.type(screen.getByLabelText(/source/i), 'test-source')
    await user.click(screen.getByRole('button', { name: /create/i }))

    // Verify error handling (toast or error message)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /create/i })).not.toBeDisabled()
    })
  })
})
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| unittest (Python) | pytest | ~2015 | Simpler test syntax, powerful fixtures, better async support, parametrization, plugin ecosystem |
| Enzyme (React testing) | React Testing Library | ~2019 | Focus on user behavior vs implementation details, better test maintainability, accessibility-first |
| Manual coverage tracking | Integrated coverage tools | ~2010 | Automated coverage measurement, HTML reports, threshold enforcement, CI integration |
| Synchronous Python tests | pytest-asyncio | ~2020 | Native async/await support, realistic FastAPI testing, no sync wrapper overhead |
| coverage --branch | coverage --line (default) | ~2018 | Line coverage sufficient for most projects, branch coverage adds complexity without proportional value |
| Manual time.time() | time.perf_counter() | Python 3.3 (2012) | High-resolution monotonic clock, immune to system time changes, accurate for performance testing |

**Deprecated/outdated:**
- **unittest.TestCase:** Verbose, requires classes, manual setUp/tearDown. Replaced by pytest's simpler function-based tests with fixtures.
- **Enzyme:** Tests React implementation details (state, lifecycle), brittle during refactors. React Testing Library tests user behavior, more maintainable.
- **jest.fn().mockReturnValue():** Still valid but jest.spyOn() provides better integration with actual module functions.
- **fireEvent (React Testing Library):** Still works but userEvent provides more realistic user interactions with timing/focus/hover.

## Open Questions

1. **Should frontend tests mock nuqs (URL state management)?**
   - What we know: Components use useQueryState from nuqs for URL state
   - What's unclear: Whether nuqs should be mocked or tested with real URL updates
   - Recommendation: Mock nuqs in component tests (simpler, faster) but consider one integration test verifying URL state updates work end-to-end

2. **How to test Server Components vs Client Components?**
   - What we know: Next.js 15 uses Server Components by default, Client Components marked with "use client"
   - What's unclear: Testing strategy for Server Components that fetch data
   - Recommendation: Focus on Client Components (forms, modals, interactive UI). Server Components are thin data fetchers - integration tests at API level sufficient

3. **Should Docker test service run tests on container start or on-demand?**
   - What we know: Need Docker service for CI-like testing
   - What's unclear: Auto-run on docker-compose up vs manual trigger via make test
   - Recommendation: On-demand via Makefile (make test) - avoids blocking startup, clearer control, matches existing pattern

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 (backend) + Jest 29.7.0 (frontend) |
| Config file | backend/pyproject.toml (pytest) + frontend/jest.config.js |
| Quick run command | `make test-quick` (skips @pytest.mark.slow) |
| Full suite command | `make test` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TEST-01 | Backend unit tests cover business logic with 80%+ coverage | unit | `pytest tests/test_cursor.py tests/test_schemas.py tests/test_config.py -v` | ✅ Partial (need coverage measurement) |
| TEST-02 | Integration tests cover all API endpoints with success/error cases | integration | `pytest tests/test_logs_crud.py tests/test_logs_list.py tests/test_export.py tests/test_analytics.py tests/test_health.py -v` | ✅ Partial (need to verify all error cases covered) |
| TEST-03 | Performance tests verify database query performance with 100k+ logs | performance | `pytest tests/test_logs_performance.py -v` | ✅ Partial (need to expand to analytics + CSV export) |
| TEST-04 | Tests verify pagination, filtering, and sorting correctness | integration | `pytest tests/test_logs_list.py tests/test_logs_performance.py::test_pagination_consistency_with_scale -v` | ✅ Exists |
| TEST-05 | All tests runnable via single command | manual verification | `make test` | ❌ Wave 0 (need to update Makefile) |

### Sampling Rate
- **Per task commit:** `make test-quick` (<10s - unit tests + fast integration tests)
- **Per wave merge:** `make test` (full suite including slow performance tests)
- **Phase gate:** Full suite green + coverage reports generated before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `backend/requirements-dev.txt` — add pytest-cov==6.0.0
- [ ] `frontend/package.json` — add jest-axe dev dependency
- [ ] `Makefile` — update test target to run both backend and frontend
- [ ] `Makefile` — add test-quick target (pytest -m "not slow")
- [ ] `Makefile` — add coverage target (pytest --cov + jest --coverage)
- [ ] `backend/pyproject.toml` — add coverage configuration (--cov=app, --cov-report)
- [ ] `frontend/jest.config.js` — add coverageThreshold and collectCoverageFrom exclusions
- [ ] `backend/tests/test_logs_performance.py` — expand to analytics and CSV export
- [ ] `frontend/__tests__/components/create-form.test.tsx` — new file
- [ ] `frontend/__tests__/components/edit-form.test.tsx` — new file
- [ ] `frontend/__tests__/components/log-detail-modal.test.tsx` — new file
- [ ] `frontend/__tests__/components/create-log-modal.test.tsx` — new file
- [ ] `frontend/__tests__/api/api-integration.test.tsx` — new file
- [ ] `frontend/__tests__/setup.ts` — add jest-axe matchers
- [ ] `docker-compose.yml` — optional: add test service (if needed for CI-like execution)

## Sources

### Primary (HIGH confidence)
- pytest documentation (https://docs.pytest.org/en/stable/) - Markers, fixtures, async testing
- pytest-cov documentation (https://pytest-cov.readthedocs.io/en/latest/) - Coverage configuration, report formats
- Jest documentation (https://jestjs.io/docs/configuration) - Coverage configuration, thresholds
- React Testing Library documentation (https://testing-library.com/docs/react-testing-library/) - Testing philosophy, best practices
- Existing backend test files (backend/tests/*.py) - Established patterns, fixture usage, async testing
- Existing frontend test infrastructure (frontend/__tests__/, jest.config.js) - Configuration, test utilities

### Secondary (MEDIUM confidence)
- coverage.py documentation (https://coverage.readthedocs.io/en/latest/) - Line vs branch coverage, HTML reports
- MSW documentation (https://mswjs.io/docs/getting-started) - API mocking approach (decided against for this scope)

### Tertiary (LOW confidence)
- None - all findings verified with official documentation or existing project code

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - pytest, Jest, React Testing Library are industry standards, versions confirmed in project
- Architecture: HIGH - patterns extracted from existing test files (conftest.py, test_logs_performance.py, test-utils.tsx)
- Pitfalls: HIGH - common issues well-documented in pytest/Jest communities, validated against existing code patterns
- Frontend testing scope: HIGH - user decisions in CONTEXT.md provide clear boundaries
- Performance thresholds: HIGH - explicit requirements in CONTEXT.md and ROADMAP.md

**Research date:** 2026-03-27
**Valid until:** 2026-04-26 (30 days - stable technologies, pytest and Jest evolve slowly)
