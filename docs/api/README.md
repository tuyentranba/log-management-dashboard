# API Documentation

REST API specification for the Logs Dashboard.

## Contents

- [contract.md](./contract.md) - Complete API reference with endpoints, query parameters, and schemas

## Quick Reference

**Base URL:** `/api`

**Endpoints:**
- `POST /logs` - Create log
- `GET /logs` - List logs (cursor paginated)
- `GET /logs/{id}` - Get single log
- `PUT /logs/{id}` - Update log
- `DELETE /logs/{id}` - Delete log
- `GET /analytics` - Get aggregated metrics
- `GET /export` - Export logs as CSV stream

See [contract.md](./contract.md) for full details including query parameters and request/response schemas.
