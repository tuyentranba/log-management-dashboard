'use client'

import { useState, useCallback } from 'react'
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
