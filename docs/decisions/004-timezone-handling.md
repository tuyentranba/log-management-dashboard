# ADR-004: Use timestamptz with UTC Normalization for Timezone Correctness

**Status:** Accepted
**Date:** 2026-03-20
**Deciders:** Development Team

## Context

Log timestamps must preserve timezone information and aggregate correctly across time zones. Without proper timezone handling, the application risks producing incorrect analytics results and ambiguous log records that undermine data integrity.

### The Problem

Logs can be generated from multiple sources operating in different timezones:
- **Server infrastructure** running in UTC (AWS, GCP, etc.)
- **Developers** working in local timezones (PST, EST, JST)
- **CI/CD pipelines** generating logs in various regions

Without timezone-aware timestamps, we encounter critical issues:

**1. Ambiguous Timestamp Meaning:**
A log entry with timestamp "2024-03-20 15:00:00" (no timezone) is ambiguous:
- Does it mean 3 PM UTC? (11 AM PST)
- Does it mean 3 PM PST? (11 PM UTC)
- Does it mean 3 PM JST? (6 AM UTC)

Without the timezone context, the same timestamp could represent three moments 8-17 hours apart.

**2. Incorrect Analytics Aggregations:**
When aggregating logs by hour using `date_trunc('hour', timestamp)`:
- Log A: "2024-03-20 15:00:00" (actually UTC)
- Log B: "2024-03-20 15:00:00" (actually PST)

These logs appear in the same hourly bucket but are actually 8 hours apart. Time-series charts and hourly aggregations produce misleading results.

**3. Date Range Filter Failures:**
User filters for "logs on March 20" but which timezone's March 20?
- March 20 in UTC spans 00:00-23:59 UTC
- March 20 in PST spans March 20 08:00 UTC - March 21 07:59 UTC
- Comparing timezone-naive "March 20" to database timestamps breaks the query logic

**4. DST Transition Bugs:**
Daylight Saving Time transitions create duplicate or missing hours with naive timestamps:
- "2024-03-10 02:30:00" during spring forward doesn't exist (clock jumps 02:00 → 03:00)
- "2024-11-03 01:30:00" during fall back occurs twice (clock goes 02:00 → 01:00)

### Technical Context

- **Database:** PostgreSQL 18 with `timestamptz` (timestamp with time zone) data type
- **Backend:** Python with `datetime` objects, SQLAlchemy 2.0, Pydantic schemas
- **Frontend:** JavaScript `Date` objects in Next.js 15 application
- **Requirement:** ANALYTICS-07 mandates explicit timezone handling for time-series aggregations

### Real-World Scenario

Consider a distributed system generating logs:
```
[api-service UTC]     2024-03-20 15:00:00 UTC "Request received"
[worker PST]          2024-03-20 15:00:00 PST "Job started"      (actually 23:00 UTC)
[database JST]        2024-03-20 15:00:00 JST "Query executed"   (actually 06:00 UTC)
```

Without timezone preservation, all three appear simultaneous when stored as "2024-03-20 15:00:00". Analytics showing "requests per hour" would incorrectly group these logs that are actually 8-17 hours apart.

## Requirements Addressed

- **DB-02:** Timestamp column uses `timestamptz` (timezone-aware) data type
- **ANALYTICS-07:** Time-series aggregations use explicit timezone handling
- **NFR-Correctness:** No timezone bugs in date range queries or analytics
- **API-07:** All API endpoints include input validation (reject timezone-naive timestamps at schema level)

## Options Considered

### Option 1: Naive Timestamps (timestamp without time zone)

**Description:** Use PostgreSQL `timestamp` (without time zone) column type. Store timestamps as entered without timezone information.

**Pros:**
- Simpler storage model
- Smaller data type (8 bytes)
- No timezone conversion logic needed
- Displays "as entered" without client-side conversion

**Cons:**
- **Ambiguous meaning:** "3 PM" in which timezone? Impossible to determine original context
- **Analytics produce wrong results:** Cannot aggregate correctly across timezones
- **Date range queries break:** Cannot compare meaningfully (3 PM PST vs 3 PM UTC)
- **Cannot represent DST transitions:** Spring forward/fall back create duplicate or missing hours
- **Violates ANALYTICS-07:** Time-series aggregations require timezone awareness
- **No chronological sorting:** Cannot reliably sort logs from multiple timezones

**Conclusion:** Rejected - fails fundamental requirement for accurate analytics and data integrity.

### Option 2: Timestamp with Local Timezone Storage (timestamptz storing original)

**Description:** Use PostgreSQL `timestamptz` column but store the timestamp in its original timezone (preserve PST as PST, JST as JST, etc.).

**Pros:**
- Preserves original timezone information
- Can display "as entered" (e.g., "logged at 3 PM PST")
- Timezone context available for forensics

**Cons:**
- **Complex aggregations:** Must normalize all timestamps to single timezone before aggregation
- **Query filters require conversion:** Date range "March 20 UTC" must convert each row's timezone
- **Cannot sort chronologically:** Sorting by timestamp column sorts by local time, not global time
- **date_trunc() produces wrong buckets:** "3 PM PST" and "3 PM JST" bucket together despite 17-hour gap
- **Performance penalty:** Every query requires timezone conversion calculation

**Example problem:**
```sql
-- Hourly aggregation with local timezone storage
SELECT date_trunc('hour', timestamp), COUNT(*)
FROM logs
GROUP BY 1;

-- Result mixes timezones in same bucket:
-- 2024-03-20 15:00 PST (actually 23:00 UTC)
-- 2024-03-20 15:00 JST (actually 06:00 UTC)
-- Both appear as "15:00" despite 17-hour difference
```

**Conclusion:** Rejected - adds complexity without meaningful benefit for log viewing use case.

### Option 3: Timestamp with UTC Normalization (timestamptz storing UTC) ✓

**Description:** Use PostgreSQL `timestamptz` column type with all timestamps normalized to UTC before storage. PostgreSQL automatically converts timezone-aware inputs to UTC.

**Pros:**
- **Unambiguous meaning:** All timestamps in database are UTC (global reference point)
- **Correct aggregations:** All times in same timezone, `date_trunc()` works correctly
- **Chronological sorting works:** Sorting by timestamp produces global chronological order
- **Standard industry practice:** AWS CloudWatch, Datadog, Splunk, Elasticsearch all use UTC storage
- **PostgreSQL best practice:** `timestamptz` is recommended type per PostgreSQL documentation
- **Efficient queries:** No per-row timezone conversion needed
- **Follows PostgreSQL semantics:** `timestamptz` always stores UTC internally regardless of input timezone

**Cons:**
- **Original timezone lost:** Cannot display "logged at 3 PM PST" (only "logged at 23:00 UTC")
- **Requires frontend conversion:** Browser must convert UTC to local timezone for display
- **Slightly complex validation:** Pydantic field validator needed to reject timezone-naive inputs
- **Developer education:** Team must understand UTC vs local time concepts

**Storage behavior:**
```sql
-- Input: 2024-03-20 15:00:00-08:00 (PST)
-- Stored: 2024-03-20 23:00:00+00:00 (UTC)

-- Input: 2024-03-20 15:00:00+09:00 (JST)
-- Stored: 2024-03-20 06:00:00+00:00 (UTC)

-- Aggregation now works correctly:
-- Bucket 06:00 UTC - logs from 15:00 JST
-- Bucket 23:00 UTC - logs from 15:00 PST
```

**Conclusion:** Accepted - correct aggregations and standard practice outweigh minor display complexity.

### Option 4: Store Both (timestamptz + timezone name column)

**Description:** Use two columns: `timestamptz` storing UTC + `VARCHAR` storing original timezone name (e.g., "America/Los_Angeles").

**Pros:**
- Preserves original timezone for display
- Enables UTC aggregations (best of both worlds)
- Supports forensics ("which timezone was the system in?")

**Cons:**
- **Storage overhead:** 8 bytes (timestamptz) + 20-30 bytes (varchar) vs 8 bytes alone
- **Complex synchronization:** Two columns must stay consistent (timezone name matches timestamp offset)
- **Overkill for use case:** Log viewing doesn't require "entered at 3 PM PST" level of detail
- **Validation complexity:** Must validate timezone name is valid (e.g., "America/Los_Angeles" exists)
- **Migration effort:** More columns to populate during bulk inserts

**Conclusion:** Rejected - storage overhead and complexity not justified for log dashboard use case. Could reconsider in v2 if user research shows demand for original timezone display.

## Decision

**We will use PostgreSQL `timestamptz` column type with UTC normalization:**

### 1. Database Column Definition

```python
# backend/app/models.py
class Log(Base):
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    # SQLAlchemy TIMESTAMP(timezone=True) → PostgreSQL timestamptz
```

**Behavior:** PostgreSQL `timestamptz` stores all timestamps as UTC internally. When inserting:
- Input: ISO 8601 with timezone (e.g., `2024-03-20T15:30:00-08:00`)
- Stored: Converted to UTC (`2024-03-20T23:30:00Z`)

### 2. API Input Validation

**Reject timezone-naive timestamps at API boundary:**

```python
# backend/app/schemas/logs.py
class LogCreate(BaseModel):
    timestamp: datetime

    @field_validator('timestamp')
    @classmethod
    def validate_timezone_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError(
                "Timestamp must include timezone. "
                "Use ISO 8601 format: 2024-03-20T15:30:00Z"
            )
        return v
```

**Accepted formats:**
- `2024-03-20T15:30:00Z` (UTC, Z suffix)
- `2024-03-20T15:30:00+00:00` (UTC, explicit offset)
- `2024-03-20T15:30:00-08:00` (PST, explicit offset)

**Rejected format:**
- `2024-03-20T15:30:00` (no timezone - ambiguous!)

### 3. Analytics Queries

**Use explicit UTC timezone in aggregations:**

```python
# backend/app/routers/analytics.py
# Time-series bucketing with explicit UTC
time_series_query = select(
    func.date_trunc(granularity, Log.timestamp).label('bucket'),
    func.count().label('count')
).where(*filters).group_by('bucket')
```

**PostgreSQL behavior:** Since `Log.timestamp` is `timestamptz` (stored as UTC), `date_trunc()` operates on UTC values automatically. All hourly/daily/weekly buckets are in UTC.

### 4. Frontend Display

**Convert UTC to browser's local timezone for user-friendly display:**

```typescript
// frontend/src/app/logs/_components/create-form.tsx
// datetime-local input with timezone conversion
<input
  type="datetime-local"
  {...register('timestamp', {
    setValueAs: (value) => {
      if (!value) return undefined
      // Convert local datetime-local to ISO 8601 with timezone
      return new Date(value).toISOString()
    }
  })}
/>
```

**Display logic:**
- Database returns: `2024-03-20T23:00:00Z` (UTC)
- JavaScript `Date.toLocaleString()` converts to user's local timezone automatically
- User in PST sees: "March 20, 2024 3:00 PM"
- User in JST sees: "March 21, 2024 8:00 AM"

### 5. Implementation Summary

| Layer | Pattern | Purpose |
|-------|---------|---------|
| Database | `timestamptz` column | Stores UTC, preserves timezone semantics |
| API Input | Pydantic validator | Rejects timezone-naive timestamps |
| API Queries | `date_trunc()` on timestamptz | UTC-based time bucketing |
| API Output | ISO 8601 with timezone | Returns `2024-03-20T23:00:00Z` |
| Frontend Input | `datetime-local` + `toISOString()` | Converts local time to UTC with timezone |
| Frontend Display | `Date.toLocaleString()` | Converts UTC to browser's local timezone |

## Consequences

### Positive

1. **Unambiguous timestamp meaning:** Every timestamp in database is UTC (global reference point). No question about "which timezone?"

2. **Correct analytics aggregations:** Time-series charts and hourly aggregations work correctly because all timestamps in same timezone. `date_trunc('hour', timestamp)` produces accurate hourly buckets.

3. **Date range filters work correctly:** Comparing UTC to UTC is straightforward. User filters "March 20-21" → backend converts to UTC range → query compares UTC timestamps.

4. **Follows PostgreSQL best practices:** PostgreSQL documentation recommends `timestamptz` over `timestamp` for exactly this reason. `timestamptz` is "what you want" according to official guidance.

5. **Pydantic validation catches bugs early:** API rejects timezone-naive timestamps at schema validation layer (HTTP 400 error), preventing corrupt data from reaching database.

6. **Standard industry pattern:** Every major observability platform uses UTC storage:
   - AWS CloudWatch stores UTC
   - Datadog stores UTC
   - Splunk stores UTC
   - Elasticsearch stores UTC
   - Prometheus stores Unix timestamps (UTC)

7. **Chronological sorting guaranteed:** Sorting by `timestamp` column produces correct global chronological order. Logs from PST, UTC, and JST sources intermix correctly.

8. **No DST bugs:** Daylight Saving Time transitions handled automatically by PostgreSQL. Spring forward/fall back don't create duplicate or missing hours in UTC.

### Negative

1. **Original timezone information lost:** Cannot display "logged at 3 PM PST" to user. Can only show "logged at 11 PM UTC" or "logged at 3 PM" (browser's local timezone).

2. **Requires frontend timezone conversion:** Frontend must convert UTC timestamps to user's local timezone for display. Adds complexity to rendering logic.

3. **Slightly more complex API validation:** Requires Pydantic `@field_validator` to enforce timezone-aware timestamps. Adds ~10 lines of validation code.

4. **Developer education needed:** Team members must understand:
   - Difference between UTC and local time
   - Why database stores UTC
   - How to send timezone-aware ISO 8601 strings
   - How JavaScript `Date` handles timezone conversion

5. **Potential user confusion:** Power users expecting to see "original timezone" may be confused when logs always display in UTC or browser's local timezone.

### Neutral

1. **PostgreSQL automatic conversion:** `timestamptz` column stores UTC internally regardless of input timezone. PostgreSQL handles conversion automatically - not a pro or con, just behavior to understand.

2. **JavaScript `Date` object semantics:** JavaScript `Date` stores milliseconds since Unix epoch (UTC) and converts to local timezone on display. This matches PostgreSQL `timestamptz` semantics well.

3. **ISO 8601 standard format:** Using ISO 8601 with timezone (e.g., `2024-03-20T15:30:00Z`) is standard format across all programming languages. No custom parsing needed.

### Technical Debt

- If future user research shows demand for "original timezone" display (e.g., "logged at 3 PM PST"), could add optional `timezone VARCHAR(50)` column in v2. Migration path exists but not needed now.

## Alternatives Rejected

### Why Not Naive Timestamps?

**Rejected because analytics aggregations produce incorrect results.**

**Concrete example of bug:**
```sql
-- Database with naive timestamps (no timezone):
INSERT INTO logs (timestamp, message) VALUES
  ('2024-03-20 15:00:00', 'Log from PST server'),  -- actually 3 PM PST = 11 PM UTC
  ('2024-03-20 15:00:00', 'Log from UTC server');  -- actually 3 PM UTC

-- Hourly aggregation:
SELECT date_trunc('hour', timestamp), COUNT(*)
FROM logs
GROUP BY 1;

-- Result shows:
-- 2024-03-20 15:00:00 | 2 logs

-- BUG: These logs are 8 hours apart but bucket together!
-- This violates ANALYTICS-07 requirement for accurate time-series data.
```

**Additional problems:**
- Cannot implement requirement ANALYTICS-07 (explicit timezone handling)
- Date range filters ambiguous (March 20 in which timezone?)
- Cannot chronologically sort logs from multiple sources
- DST transitions create duplicate or missing hours

### Why Not Local Timezone Storage?

**Rejected because aggregating across timezones is overly complex.**

**Concrete example of problem:**
```sql
-- Database with timestamptz storing original timezone:
INSERT INTO logs (timestamp) VALUES
  ('2024-03-20 15:00:00-08:00'),  -- 3 PM PST (stored as 15:00 PST)
  ('2024-03-20 15:00:00+09:00');  -- 3 PM JST (stored as 15:00 JST)

-- Hourly aggregation (naive):
SELECT date_trunc('hour', timestamp), COUNT(*)
FROM logs
GROUP BY 1;

-- Result mixes timezones:
-- 2024-03-20 15:00 | 2 logs

-- BUG: These are 17 hours apart but bucket to same hour!
```

**Correct aggregation requires normalization first:**
```sql
SELECT date_trunc('hour', timestamp AT TIME ZONE 'UTC'), COUNT(*)
FROM logs
GROUP BY 1;
```

But if we always normalize to UTC for queries, why not store as UTC in the first place? Simpler to store UTC than convert on every query.

### Why Not Store Both Columns?

**Rejected because storage overhead isn't justified for log viewing use case.**

**Analysis:**
- **Storage cost:** ~20-30 bytes per row (varchar timezone name)
- **Benefit for users:** Can display "logged at 3 PM PST" instead of "logged at 11 PM UTC"
- **User research needed:** No evidence users need this level of detail

For a log dashboard, users care about:
1. What happened? (message)
2. When did it happen? (timestamp, timezone-converted for display)
3. How severe? (severity)
4. Where did it come from? (source)

"Which timezone was the log originally in?" is rarely relevant. Users in PST naturally see timestamps in PST. Users in JST see timestamps in JST. The automatic browser conversion provides sufficient context.

**Decision:** Defer timezone name storage to v2 if user research shows demand. For MVP, UTC-only storage is sufficient and simpler.

## References

### Implementation Files
- **Model definition:** `backend/app/models.py` (Log model with `TIMESTAMP(timezone=True)`)
- **Schema validation:** `backend/app/schemas/logs.py` (LogCreate with timezone validator)
- **Analytics queries:** `backend/app/routers/analytics.py` (`date_trunc` with timestamptz)
- **Frontend input:** `frontend/src/app/logs/_components/create-form.tsx` (datetime-local with `toISOString()`)
- **Frontend display:** Log table components automatically convert UTC via JavaScript `Date`

### Test Coverage
- `backend/tests/test_schemas.py` - `test_timestamp_timezone_validation()` verifies rejection of naive timestamps
- `backend/tests/test_logs.py` - Integration tests verify timezone preservation through API

### Related Decisions
- **Plan 01-01 in STATE.md:** Original database schema decision documenting `TIMESTAMP(timezone=True)` choice
- **Plan 05-01 in STATE.md:** Analytics aggregation patterns with `date_trunc()` on timestamptz

### External Documentation
- [PostgreSQL Date/Time Types](https://www.postgresql.org/docs/18/datatype-datetime.html) - Official PostgreSQL 18 documentation on `timestamptz` vs `timestamp`
- [PostgreSQL Timestamp Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This#Don.27t_use_timestamp_.28without_time_zone.29) - PostgreSQL Wiki explaining why to avoid `timestamp without time zone`
- [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) - International standard for date/time representation with timezone
- [Python datetime with timezone](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects) - Python documentation on timezone-aware vs naive datetime objects
- [MDN Date.toISOString()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toISOString) - JavaScript UTC timestamp conversion

### Architecture Context
This decision integrates with:
- **ADR-002** (if exists): Database indexing strategy (BRIN index on timestamptz column for time-series efficiency)
- **ADR-005**: Frontend architecture patterns (Server Components for SSR, timezone conversion in client)
