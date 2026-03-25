// Mirror backend/app/schemas/logs.py

export type Severity = 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'

export interface LogResponse {
  id: number
  timestamp: string  // ISO 8601 with timezone (e.g., "2024-03-20T15:30:00Z")
  message: string
  severity: Severity
  source: string
}

export interface LogListResponse {
  data: LogResponse[]
  next_cursor: string | null  // Base64-encoded cursor token
  has_more: boolean
}

export interface LogCreate {
  timestamp: string  // ISO 8601 with timezone
  message: string
  severity: Severity
  source: string
}

export interface LogFilters {
  search?: string
  severity?: Severity[]
  source?: string
  date_from?: string  // ISO 8601 date (e.g., "2024-03-20")
  date_to?: string
  sort?: 'timestamp' | 'severity' | 'source'
  order?: 'asc' | 'desc'
}

// Analytics Dashboard Types (mirror backend AnalyticsResponse schema)

export interface AnalyticsFilters {
  date_from: string  // ISO 8601 with timezone (REQUIRED)
  date_to: string    // ISO 8601 with timezone (REQUIRED)
  severity?: Severity[]
  source?: string
}

export interface TimeSeriesDataPoint {
  timestamp: string  // ISO 8601 with timezone from PostgreSQL date_trunc
  count: number
}

export interface SeverityDistributionPoint {
  severity: Severity
  count: number
}

export interface AnalyticsResponse {
  summary: {
    total: number
    by_severity: {
      INFO: number
      WARNING: number
      ERROR: number
      CRITICAL: number
    }
  }
  time_series: TimeSeriesDataPoint[]
  severity_distribution: SeverityDistributionPoint[]
  granularity: 'hour' | 'day' | 'week'
}
