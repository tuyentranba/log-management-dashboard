# Database Schema

PostgreSQL database with single `logs` table optimized for time-series queries.

```sql
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,  -- Timezone-aware timestamp
    message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,   -- INFO, WARNING, ERROR, CRITICAL
    source VARCHAR(100) NOT NULL
);

-- BRIN index for time-series range queries (analytics)
CREATE INDEX idx_logs_timestamp_brin
    ON logs USING BRIN (timestamp);

-- Composite B-tree for filtered pagination
CREATE INDEX idx_logs_composite
    ON logs (timestamp, severity, source);
```

**Index strategy:**
- **BRIN on timestamp**: Block-level min/max index skips 95%+ of blocks for time-range queries, 0.1% storage overhead
- **Composite B-tree on (timestamp, severity, source)**: Enables multi-column filtered queries with direct seeks, 5% storage overhead

**Total storage overhead:** ~5% for both indexes combined
