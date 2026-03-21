# Knowledge Base

A living document tracking concepts, decisions, and learnings for the Logs Dashboard project.

---

## Database & Performance

### Indexing Strategies

#### B-tree Indexes
- **What**: Balanced tree structure, PostgreSQL's default index type
- **Performance**: O(log n) lookup time
- **Size**: Larger, stores all indexed values
- **Best for**: Equality and range queries (=, <, <=, >, >=, BETWEEN)
- **Use cases in this project**:
  - `user_id` columns (random access)
  - `severity` (categorical lookup)
  - `source` (string equality)
  - Foreign keys

```sql
CREATE INDEX idx_logs_severity ON logs USING btree (severity);
CREATE INDEX idx_logs_source ON logs USING btree (source);
```

#### BRIN Indexes (Block Range INdex)
- **What**: Stores min/max values for consecutive physical blocks
- **Performance**: O(n) worst case, but very fast when data is naturally ordered
- **Size**: Tiny (often 1000x smaller than B-tree)
- **Best for**: Large tables with natural clustering (timestamps, sequential IDs)
- **Use cases in this project**:
  - `timestamp` column (time-series data)
  - `id` (sequential primary key)

```sql
CREATE INDEX idx_logs_timestamp ON logs USING brin (timestamp);
```

**Trade-offs**:
- BRIN: Minimal maintenance overhead, perfect for append-only logs
- B-tree: Exact lookups but higher write/storage cost

**Decision for logs table**:
- Use **BRIN for timestamp** (logs are append-only, naturally ordered)
- Use **B-tree for severity/source** (random access patterns)

---

## Architecture Patterns

### Async Database Operations + Dependency Injection

#### Why Async/Await?

**The Problem with Synchronous I/O**:
```python
# Synchronous (blocking)
result = db.query(...)  # Thread BLOCKS waiting for database
return result
```
- Thread is blocked during I/O operations (database queries, file reads, network calls)
- 1000 concurrent requests = 1000 threads = high memory usage
- Threads just sit idle waiting for I/O

**The Async Solution**:
```python
# Asynchronous (non-blocking)
async def get_logs():
    result = await db.query(...)  # Thread released during I/O
    return result
```
- Thread is released during I/O, can handle other requests
- 1000 concurrent requests = 10-50 threads = efficient resource usage
- Same throughput with far fewer resources

**Real-world example for logs dashboard**:
- Query 100k logs takes 200ms
- 100 simultaneous users:
  - Sync: 100 threads, ~500MB memory, blocks on slow queries
  - Async: 5 threads, ~25MB memory, handles load gracefully

#### Why Dependency Injection?

**Without DI (manual management)**:
```python
@app.get("/logs")
def get_logs():
    db = SessionLocal()  # Manual connection
    try:
        logs = db.query(Log).all()
        return logs
    finally:
        db.close()  # Must remember to close!
```

**Problems**:
- Boilerplate in every endpoint
- Easy to forget cleanup → connection leaks
- Hard to test (database hardcoded)
- No centralized connection pool management

**With DI (FastAPI pattern)**:
```python
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        # Automatically closes after request

@app.get("/logs")
async def get_logs(db: AsyncSession = Depends(get_db)):
    logs = await db.query(Log).all()
    return logs
```

**Benefits**:
- ✅ Automatic cleanup (even on exceptions)
- ✅ No boilerplate (just declare dependency)
- ✅ Easy to test (inject mock database)
- ✅ Single source of truth for connection logic
- ✅ Centralized connection pooling

#### Complete Pattern

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 1. Create async engine with connection pool
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,        # 20 reusable connections
    max_overflow=10,     # +10 overflow connections
    echo=True            # Log queries (dev only)
)

# 2. Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Dependency provider
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# 4. Use in endpoints
@app.get("/logs")
async def get_logs(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    result = await db.execute(
        select(Log).offset(skip).limit(limit)
    )
    return result.scalars().all()
```

**Performance comparison (100 concurrent users)**:

| Pattern | Threads | Memory | Crashes at |
|---------|---------|--------|------------|
| Sync without pooling | 100 | ~500MB | 200 users |
| Sync with pooling | 20 blocked | ~100MB | 500 users |
| Async with pooling | 2-5 active | ~25MB | 5000+ users |

**Decision**: Use async + DI pattern for all database operations to maximize concurrency and resource efficiency.

### API Design

#### Pagination Response Formats

**Direct Array (metadata in headers)**:
- Returns `[{...}, {...}]` directly
- Pagination info in HTTP headers (X-Total-Count, Link, etc.)
- Pros: Simpler, standard practice (GitHub)
- Cons: Headers harder to access, can't include extra context

**Envelope Format (metadata in body)** ⭐️:
```json
{
  "data": [...],
  "pagination": { "page": 1, "total_items": 1000, "has_next": true },
  "filters_applied": { "severity": "ERROR" }
}
```
- All info in response body
- Pros: Easy access, can include filters/aggregations, consistent structure
- Cons: Extra nesting

**Decision**: Use envelope format for logs dashboard (better for filtering context and frontend needs)

### Error Handling

*To be documented as patterns emerge*

### Testing Strategy

*To be documented during implementation*

---

## Technical Decisions Log

| Date | Topic | Decision | Rationale |
|------|-------|----------|-----------|
| 2026-03-20 | Timestamp indexing | Use BRIN index | Logs are append-only time-series data, BRIN provides 1000x smaller index with excellent performance for range queries |
| 2026-03-20 | Categorical indexing | Use B-tree for severity/source | Random access patterns require exact lookups |
| 2026-03-20 | Database pattern | Async + Dependency Injection | Handle 1000+ concurrent users with minimal resources, automatic connection cleanup, easier testing |
| 2026-03-20 | API pagination format | Envelope with metadata in body | Need to return filters applied, easier frontend access, can include aggregations |

---

## Concepts to Explore

- [x] Database connection pooling strategies
- [x] FastAPI async/await patterns
- [ ] PostgreSQL query optimization techniques
- [ ] React Server Components vs Client Components
- [ ] CSV export streaming vs buffered
- [ ] Chart library selection (Chart.js vs Recharts vs D3)
- [ ] Docker multi-stage builds
- [ ] Test data generation strategies
- [ ] Alembic migrations best practices
- [ ] SQLAlchemy 2.0 query patterns

---

## Questions & Answers

### Q: Why not use B-tree for everything?
**A**: BRIN indexes are ideal for timestamp columns on large tables because:
1. Logs are naturally ordered by time (append-only)
2. 1000x smaller index size = less I/O, faster inserts
3. Range queries (date filters) still very fast with clustered data
4. Minimal maintenance overhead

### Q: When should I rebuild indexes?
**A**:
- B-tree: Automatically maintained, rarely needs rebuilding
- BRIN: May need periodic rebuild if data becomes unordered (not an issue for append-only logs)

### Q: Why use async for database but the queries still take the same time?
**A**: Async doesn't make individual queries faster - it makes your server handle MORE concurrent queries efficiently:
- Sync: 100 users → 100 threads → 500MB memory → server crashes at 200 users
- Async: 100 users → 5 threads → 25MB memory → handles 5000+ users

Each query still takes 200ms, but you can handle 50x more concurrent requests.

### Q: What's the difference between `yield` and `return` in dependency functions?
**A**:
- `yield`: Provides value to endpoint, then runs cleanup code after request completes
- `return`: Just returns value, no cleanup

```python
async def get_db():
    db = AsyncSessionLocal()
    yield db          # ← Endpoint uses db
    await db.close()  # ← Runs after endpoint completes (even if error)
```

### Q: Do I need async everywhere or just database operations?
**A**: Start with async for I/O operations (database, file reads, external APIs), but you don't need to make pure computation async:
- ✅ Async: Database queries, HTTP requests, file I/O
- ❌ Don't need async: JSON serialization, data validation, calculations

FastAPI can mix sync and async endpoints - it automatically runs sync endpoints in thread pools.

---

## Resources & References

### PostgreSQL
- [BRIN Indexes Documentation](https://www.postgresql.org/docs/current/brin-intro.html)
- [Index Types Comparison](https://www.postgresql.org/docs/current/indexes-types.html)
- [Connection Pooling Best Practices](https://www.postgresql.org/docs/current/runtime-config-connection.html)

### FastAPI
- [Official Documentation](https://fastapi.tiangolo.com/)
- [Async/Await Guide](https://fastapi.tiangolo.com/async/)
- [Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Database Sessions](https://fastapi.tiangolo.com/tutorial/sql-databases/)

### SQLAlchemy
- [Async I/O Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Connection Pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- [Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)

### Next.js
- [Official Documentation](https://nextjs.org/docs)

---

*Last updated: 2026-03-20*
