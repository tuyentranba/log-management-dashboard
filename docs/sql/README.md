# SQL Documentation

PostgreSQL database schema and query patterns.

## Contents

- [schema.md](./schema.md) - Table definitions, indexes, and storage strategy

## Schema Overview

**Tables:**
- `logs` - Single table storing all log entries with timestamp, message, severity, source

**Indexes:**
- `idx_logs_timestamp_brin` - BRIN index for time-series range queries (0.1% storage)
- `idx_logs_composite` - Composite B-tree on (timestamp, severity, source) for filtered pagination (5% storage)

**Total storage overhead:** ~5%

See [schema.md](./schema.md) for complete SQL definitions and index strategy rationale.
