'use client'

import { useState, useCallback, useEffect } from 'react'
import { LogResponse, LogListResponse, LogFilters } from '@/lib/types'
import { fetchLogs } from '@/lib/api'

export function useInfiniteScroll(
  initialData: LogListResponse,
  filters: LogFilters = {}
) {
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
        const response = await fetchLogs(filters, null, 50)
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
      const response = await fetchLogs(filters, cursor)
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
