# Testing Guide

Comprehensive testing documentation for the Logs Dashboard project.

## Overview

The project has comprehensive test coverage for both backend and frontend components, demonstrating production-ready quality with automated validation.

**Coverage Targets:**
- Backend: 80%+ line coverage (measured by pytest-cov)
- Frontend: 80%+ line coverage (measured by Jest)

**Test Philosophy:**
- **Integration over unit:** Tests validate real behavior with real database and API calls (mocking only external dependencies)
- **Minimal mocking:** Backend tests use real PostgreSQL database for accurate validation
- **User-focused frontend tests:** Tests validate user interactions and accessibility (not implementation details)
- **Performance validation:** Hard thresholds ensure queries meet production requirements (<500ms pagination, <2s analytics)
- **Coverage as visibility:** 80% target demonstrates quality without over-testing trivial code

## Quick Start

Run all tests (backend + frontend):
```bash
make test
```

Run quick tests (skip slow performance tests):
```bash
make test-quick
```

Run tests with coverage reports:
```bash
make coverage
```

## Backend Testing

### Test Organization

Tests located in `backend/tests/` directory:

| File | Purpose | Test Count |
|------|---------|------------|
| `test_config.py` | Configuration loading and validation | 8 tests |
| `test_cursor.py` | Cursor pagination utilities | 7 tests |
| `test_schemas.py` | Pydantic schema validation | 9 tests |
| `test_health.py` | Health endpoint integration tests | 3 tests |
| `test_logs_crud.py` | CRUD operations (POST, GET, PUT, DELETE) | 18 tests |
| `test_logs_list.py` | List endpoint with filtering and sorting | 31 tests |
| `test_export.py` | CSV export streaming | 15 tests |
| `test_analytics.py` | Analytics aggregations | 12 tests |
| `test_logs_performance.py` | Performance validation with 100k logs (marked `@pytest.mark.slow`) | 4 tests |

**Total:** 107 tests

### Running Backend Tests

**All backend tests:**
```bash
docker-compose exec backend pytest tests/ -v
```

**Specific test file:**
```bash
docker-compose exec backend pytest tests/test_logs_crud.py -v
```

**Quick tests (exclude slow performance tests):**
```bash
docker-compose exec backend pytest tests/ -v -m "not slow"
```

**With coverage:**
```bash
docker-compose exec backend pytest tests/ --cov=app --cov-report=term --cov-report=html
```

Coverage report generated at `backend/htmlcov/index.html` - open in browser for line-by-line analysis.

### Performance Test Thresholds

Performance tests (`test_logs_performance.py`) validate query execution times with 100k logs:

| Test | Threshold | Validates |
|------|-----------|-----------|
| `test_pagination_performance_at_page_100` | <500ms | Cursor pagination efficiency at deep pages |
| `test_analytics_query_performance_with_100k_logs` | <2000ms | date_trunc and GROUP BY aggregation performance |
| `test_csv_export_performance_with_large_filtered_dataset` | <3000ms | Streaming response memory efficiency with filters |
| `test_pagination_with_multi_filter_combination` | <500ms avg | Composite index utilization for complex queries |

Tests fail if thresholds are exceeded, preventing performance regressions.

**Note:** Performance tests are marked with `@pytest.mark.slow` and skipped by `make test-quick` for faster development feedback.

## Frontend Testing

### Test Organization

Tests located in `frontend/__tests__/` directory:

| File | Purpose |
|------|---------|
| `components/create-form.test.tsx` | Create log form validation and submission |
| `components/edit-form.test.tsx` | Edit log form pre-population and updates |
| `components/log-detail-modal.test.tsx` | Modal view/edit mode toggle |
| `api/api-integration.test.tsx` | API client functions with mocked fetch |

### Running Frontend Tests

**All frontend tests:**
```bash
docker-compose exec frontend npm test -- --passWithNoTests
```

**Specific test file:**
```bash
docker-compose exec frontend npm test -- --testPathPattern=create-form.test.tsx
```

**With coverage:**
```bash
docker-compose exec frontend npm test -- --coverage --passWithNoTests
```

Coverage report generated at `frontend/coverage/lcov-report/index.html`.

**Watch mode (for development):**
```bash
docker-compose exec frontend npm test -- --watch
```

## Test Configuration

### Backend (pytest + pytest-cov)

Configuration in `backend/pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # Automatic async test detection
testpaths = ["tests"]
markers = ["slow: marks tests as slow (deselect with '-m \"not slow\"')"]

[tool.coverage.run]
source = ["app"]
omit = ["app/tests/*", "app/alembic/*", "*/conftest.py"]

[tool.coverage.report]
skip_empty = true
precision = 2
```

### Frontend (Jest + React Testing Library)

Configuration in `frontend/jest.config.js`:

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({ dir: './' })

const customJestConfig = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/__tests__/setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testPathIgnorePatterns: ['/node_modules/', '/.next/'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.tsx',
    '!src/components/ui/**',
  ],
}

export default createJestConfig(customJestConfig)
```

## Coverage Reports

### Viewing Coverage Reports

After running `make coverage`, open HTML reports:

**Backend:**
```bash
open backend/htmlcov/index.html  # macOS
xdg-open backend/htmlcov/index.html  # Linux
```

**Frontend:**
```bash
open frontend/coverage/lcov-report/index.html  # macOS
xdg-open frontend/coverage/lcov-report/index.html  # Linux
```

### Interpreting Coverage

Coverage reports show:
- **Green lines:** Executed by tests
- **Red lines:** Not executed by tests
- **Yellow lines:** Partially covered (branch not taken)

**Current coverage (Phase 6):**
- Backend: 80.00% (335 statements, 67 missed)
- Frontend: Target 80%+ (Phase 6 Plan 02)

## Test Data Generation

Performance tests use `bulk_insert_mappings()` for efficient test data generation:

```python
# Generate 100k logs in <2 seconds
logs = [{
    "timestamp": base_time - timedelta(seconds=i * 26),
    "message": random.choice(messages),
    "severity": random.choices(severities, weights=[70, 20, 8, 2])[0],
    "source": random.choice(sources)
} for i in range(100000)]

await db.run_sync(lambda session: session.bulk_insert_mappings(Log, logs))
```

This approach separates CPU-bound work (data generation) from I/O-bound work (database insert) for maximum performance.

## Common Issues

### Issue: `ModuleNotFoundError` in backend tests

**Cause:** Python path not configured correctly.

**Solution:** Run tests via `docker-compose exec` (not `docker exec`) to inherit correct environment.

### Issue: Frontend tests fail with "Cannot find module"

**Cause:** `node_modules` not installed or stale.

**Solution:**
```bash
docker-compose exec frontend npm install
docker-compose restart frontend
```

### Issue: Performance tests fail with "took too long"

**Cause:** Database not seeded with 100k logs, or system under load.

**Solution:**
```bash
make seed  # Ensure 100k logs exist
# Run tests in isolated environment (close other apps)
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Install dependencies
docker-compose up -d
docker-compose exec backend pip install -r requirements-dev.txt
docker-compose exec frontend npm install

# Run tests with coverage
docker-compose exec backend pytest tests/ --cov=app --cov-report=xml
docker-compose exec frontend npm test -- --coverage --coverageReporters=cobertura

# Check coverage thresholds
docker-compose exec backend coverage report --fail-under=80
```

## Related Documentation

- [README.md](../README.md) - Quick start and project overview
- [docs/decisions/](./decisions/) - Architecture decisions affecting test strategy
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design and component interactions

---

*Last updated: 2026-03-27 (Phase 6 backend testing complete)*
