'use client'

import { useState, useCallback, useEffect } from 'react'
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

  // Refetch when filters change (but not on initial mount since we have initialData)
  const [isFirstRender, setIsFirstRender] = useState(true)

  useEffect(() => {
    if (isFirstRender) {
      setIsFirstRender(false)
      return
    }

    const refetch = async () => {
      setIsLoading(true)
      try {
        const apiFilters = convertFiltersForAPI(filters)
        const response = await fetchLogs(apiFilters, null, 50)
        setLogs(response.data)
        setCursor(response.next_cursor)
        setHasMore(response.has_more)
      } catch (error) {
        console.error('Failed to refetch logs:', error)
      } finally {
        setIsLoading(false)
      }
    }

    refetch()
  }, [
    filters.search,
    filters.severity?.join(','),
    filters.source,
    filters.date_from,
    filters.date_to,
    filters.sort,
    filters.order,
  ])

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
