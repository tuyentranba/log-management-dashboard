import { LogFilters, LogListResponse, LogResponse, LogCreate, AnalyticsFilters, AnalyticsResponse } from './types'
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
  if (filters.date_from) params.append('date_from', filters.date_from)
  if (filters.date_to) params.append('date_to', filters.date_to)
  if (filters.sort) params.append('sort', filters.sort)
  if (filters.order) params.append('order', filters.order)

  const url = `${API_URL}/api/logs?${params}`
  console.log('[api.fetchLogs] Fetching URL:', url)
  console.log('[api.fetchLogs] Filters:', filters)
  const response = await fetch(url)

  if (!response.ok) {
    console.error('[api.fetchLogs] Fetch failed:', response.status, response.statusText)
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

export async function exportLogs(filters: LogFilters): Promise<void> {
  const params = new URLSearchParams()

  // Build filter parameters (same pattern as fetchLogs, including search per WYSIWYG)
  if (filters.search) params.append('search', filters.search)
  if (filters.severity) {
    filters.severity.forEach(s => params.append('severity', s))
  }
  if (filters.source) params.append('source', filters.source)
  if (filters.date_from) params.append('date_from', filters.date_from)
  if (filters.date_to) params.append('date_to', filters.date_to)
  if (filters.sort) params.append('sort', filters.sort)
  if (filters.order) params.append('order', filters.order)

  const url = `${API_URL}/api/export?${params}`
  const response = await fetch(url)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Export failed: ${response.status}`)
  }

  // Convert streaming response to blob
  const blob = await response.blob()

  // Extract filename from Content-Disposition header
  const contentDisposition = response.headers.get('Content-Disposition')
  let filename = 'logs.csv'  // fallback
  if (contentDisposition) {
    const matches = /filename=([^;]+)/.exec(contentDisposition)
    if (matches?.[1]) {
      filename = matches[1].trim()
    }
  }

  // Trigger browser download
  const downloadUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()

  // Cleanup
  document.body.removeChild(link)
  URL.revokeObjectURL(downloadUrl)
}

export async function fetchAnalytics(
  filters: AnalyticsFilters
): Promise<AnalyticsResponse> {
  const params = new URLSearchParams()

  // Required parameters (enforced by backend - returns 400 if missing)
  if (!filters.date_from || !filters.date_to) {
    throw new Error('Date range is required for analytics')
  }
  params.append('date_from', filters.date_from)
  params.append('date_to', filters.date_to)

  // Optional parameters
  if (filters.severity) {
    filters.severity.forEach(s => params.append('severity', s))
  }
  if (filters.source) {
    params.append('source', filters.source)
  }

  const url = `${API_URL}/api/analytics?${params}`
  const response = await fetch(url)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Failed to fetch analytics: ${response.status}`)
  }

  return response.json()
}
