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

  console.log('[useInfiniteScroll] Render - filters:', filters)
  console.log('[useInfiniteScroll] Render - filtersKey:', filtersKey)

  // Debug: Track when filtersKey changes
  useEffect(() => {
    console.log('[useInfiniteScroll DEBUG] FiltersKey useEffect fired! New value:', filtersKey)
  }, [filtersKey])

  useEffect(() => {
    // Skip refetch on initial mount (we already have initialData from SSR)
    if (isFirstRender.current) {
      isFirstRender.current = false
      console.log('[useInfiniteScroll] Initial mount - skipping refetch')
      return
    }

    console.log('[useInfiniteScroll] Filters changed, refetching...', filters)

    const refetch = async () => {
      setIsLoading(true)
      const startTime = Date.now()

      try {
        const apiFilters = convertFiltersForAPI(filters)
        console.log('[useInfiniteScroll] Fetching with filters:', apiFilters)

        // Fetch data and ensure minimum 500ms loading display
        const [response] = await Promise.all([
          fetchLogs(apiFilters, null, 50),
          new Promise(resolve => setTimeout(resolve, 500))
        ])

        console.log('[useInfiniteScroll] Received', response.data.length, 'logs')
        setLogs(response.data)
        setCursor(response.next_cursor)
        setHasMore(response.has_more)
      } catch (error) {
        console.error('[useInfiniteScroll] Failed to refetch logs:', error)
        // Still respect minimum duration even on error
        const elapsed = Date.now() - startTime
        if (elapsed < 500) {
          await new Promise(resolve => setTimeout(resolve, 500 - elapsed))
        }
      } finally {
        setIsLoading(false)
      }
    }

    refetch()
  }, [filtersKey]) // Use serialized key for reliable change detection

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
