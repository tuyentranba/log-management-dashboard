# API Contract

RESTful API exposing log CRUD operations, analytics, and export endpoints.

| Method | Path | Request | Response | Description |
|--------|------|---------|----------|-------------|
| **POST** | `/api/logs` | `LogCreate` | `LogResponse` (201) | Create new log entry |
| **GET** | `/api/logs` | Query params | `LogListResponse` | List logs with cursor pagination |
| **GET** | `/api/logs/{id}` | - | `LogResponse` | Get single log by ID |
| **PUT** | `/api/logs/{id}` | `LogCreate` | `LogResponse` | Update log (all fields required) |
| **DELETE** | `/api/logs/{id}` | - | 204 No Content | Delete log |
| **GET** | `/api/analytics` | Query params | `AnalyticsResponse` | Get aggregated metrics |
| **GET** | `/api/export` | Query params | CSV stream | Export filtered logs as CSV |

**List logs query parameters:**
- `limit` (int, default 50): Page size (max 100)
- `cursor` (string, optional): Pagination cursor from previous response
- `severity` (string, optional): Filter by severity (INFO, WARNING, ERROR, CRITICAL)
- `source` (string, optional): Filter by source
- `date_from` (ISO8601, optional): Filter logs after timestamp
- `date_to` (ISO8601, optional): Filter logs before timestamp
- `search` (string, optional): Search message content (case-insensitive)

**Analytics query parameters:**
- `date_from` (ISO8601, required): Start of date range
- `date_to` (ISO8601, required): End of date range
- `severity` (string, optional): Filter by severity
- `source` (string, optional): Filter by source

**Schemas:**

```json
// LogCreate (request body for POST/PUT)
{
  "timestamp": "2024-03-20T15:30:00Z",  // ISO 8601 with timezone
  "message": "User authentication failed",
  "severity": "ERROR",  // INFO | WARNING | ERROR | CRITICAL
  "source": "auth-service"
}

// LogResponse (single log)
{
  "id": 12345,
  "timestamp": "2024-03-20T15:30:00Z",
  "message": "User authentication failed",
  "severity": "ERROR",
  "source": "auth-service"
}

// LogListResponse (paginated list)
{
  "data": [LogResponse, ...],
  "next_cursor": "eyJ0aW1lc3RhbXAiOiAiMjAyNC0wMy0yMFQxNTozMDowMFoiLCAiaWQiOiAxMjM0NX0=",
  "has_more": true
}
```
