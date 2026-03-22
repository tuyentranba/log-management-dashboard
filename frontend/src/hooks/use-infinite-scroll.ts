'use client'

import { useState, useCallback, useEffect, useRef } from 'react'
import { LogResponse, LogListResponse, LogFilters } from '@/lib/types'
import { fetchLogs } from '@/lib/api'
import { useLogFilters } from './use-log-filters'

/**
 * Convert nuqs filter state (with null) to LogFilters type (with undefined).
 * Adds type assertions for severity, sort, and order to match the API types.
 */
function convertFiltersForAPI(filters: ReturnType<typeof useLogFilters>[0]): LogFilters {
  return {
    search: filters.search ?? undefined,
    severity: (filters.severity ?? undefined) as LogFilters['severity'],
    source: filters.source ?? undefined,
    date_from: filters.date_from ?? undefined,
    date_to: filters.date_to ?? undefined,
    sort: (filters.sort ?? undefined) as LogFilters['sort'],
    order: (filters.order ?? undefined) as LogFilters['order'],
  }
}

export function useInfiniteScroll(initialData: LogListResponse) {
  const [filters] = useLogFilters()
  const [logs, setLogs] = useState<LogResponse[]>(initialData.data)
  const [cursor, setCursor] = useState<string | null>(initialData.next_cursor)
  const [hasMore, setHasMore] = useState(initialData.has_more)
  const [isLoading, setIsLoading] = useState(false)

  // Use ref to skip initial mount without causing extra renders
  const isFirstRender = useRef(true)

  // Serialize filters for dependency comparison
  // This ensures React detects changes even with complex objects/arrays
  const filtersKey = JSON.stringify({
    search: filters.search,
    severity: filters.severity,
    source: filters.source,
    date_from: filters.date_from,
    date_to: filters.date_to,
    sort: filters.sort,
    order: filters.order,
  })

  console.log('[useInfiniteScroll] Current filters:', filters)
  console.log('[useInfiniteScroll] FiltersKey:', filtersKey)

  // Sync state with SSR data when initialData changes (e.g., when URL params change and Next.js re-fetches)
  useEffect(() => {
    console.log('[useInfiniteScroll] Syncing with new initialData:', initialData.data.length, 'logs')
    setLogs(initialData.data)
    setCursor(initialData.next_cursor)
    setHasMore(initialData.has_more)
  }, [initialData])

  const loadMore = useCallback(async () => {
    if (!hasMore || isLoading) return

    setIsLoading(true)
    try {
      const apiFilters = convertFiltersForAPI(filters)
      const response = await fetchLogs(apiFilters, cursor)
      setLogs(prev => [...prev, ...response.data])
      setCursor(response.next_cursor)
      setHasMore(response.has_more)
    } catch (error) {
      console.error('Failed to load more logs:', error)
    } finally {
      setIsLoading(false)
    }
  }, [cursor, hasMore, isLoading, filters])

  return { logs, hasMore, isLoading, loadMore }
}
