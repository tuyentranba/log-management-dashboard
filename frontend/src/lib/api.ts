import { LogFilters, LogListResponse, LogResponse, LogCreate } from './types'
import { API_URL } from './constants'

export async function fetchLogs(
  filters: LogFilters = {},
  cursor?: string | null,
  limit: number = 50
): Promise<LogListResponse> {
  const params = new URLSearchParams()

  if (cursor) params.append('cursor', cursor)
  params.append('limit', limit.toString())

  if (filters.search) params.append('search', filters.search)
  if (filters.severity) {
    filters.severity.forEach(s => params.append('severity', s))
  }
  if (filters.source) params.append('source', filters.source)
  // Convert simple date format (YYYY-MM-DD) to ISO 8601 datetime (YYYY-MM-DDTHH:MM:SSZ)
  if (filters.date_from) params.append('date_from', `${filters.date_from}T00:00:00Z`)
  if (filters.date_to) params.append('date_to', `${filters.date_to}T23:59:59Z`)
  if (filters.sort) params.append('sort', filters.sort)
  if (filters.order) params.append('order', filters.order)

  const url = `${API_URL}/api/logs?${params}`
  const response = await fetch(url)

  if (!response.ok) {
    throw new Error(`Failed to fetch logs: ${response.status}`)
  }

  return response.json()
}

export async function fetchLogById(id: number): Promise<LogResponse> {
  const url = `${API_URL}/api/logs/${id}`
  const response = await fetch(url)

  if (!response.ok) {
    throw new Error(`Failed to fetch log ${id}: ${response.status}`)
  }

  return response.json()
}

export async function createLog(data: LogCreate): Promise<LogResponse> {
  const url = `${API_URL}/api/logs`
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Failed to create log: ${response.status}`)
  }

  return response.json()
}
