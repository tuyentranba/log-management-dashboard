'use client'

import { LogListResponse } from '@/lib/types'
import { LogTable } from './log-table'
import { SkeletonRows } from './skeleton-rows'
import { FilterChip } from './filter-chip'
import { useInfiniteScroll } from '@/hooks/use-infinite-scroll'
import { useLogFilters } from '@/hooks/use-log-filters'

interface LogListProps {
  initialData: LogListResponse
  onRefetch?: (refetch: () => void) => void
}

export function LogList({ initialData, onRefetch }: LogListProps) {
  const [filters, setFilters] = useLogFilters()
  const { logs, hasMore, isLoading, loadMore, refetch } = useInfiniteScroll(initialData)

  // Expose refetch function to parent
  if (onRefetch) {
    onRefetch(refetch)
  }

  if (logs.length === 0 && !isLoading) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-medium mb-2">No logs match your filters</h2>
        <p className="text-slate-600 mb-4">Try adjusting your search criteria or clear filters.</p>
      </div>
    )
  }

  const activeFilters = []
  if (filters.search) activeFilters.push({ label: 'Search', value: filters.search, key: 'search' })
  if (filters.severity?.length) {
    filters.severity.forEach(s => activeFilters.push({ label: 'Severity', value: s, key: `severity-${s}` }))
  }
  if (filters.source) activeFilters.push({ label: 'Source', value: filters.source, key: 'source' })
  if (filters.date_from) activeFilters.push({ label: 'From', value: filters.date_from, key: 'date_from' })
  if (filters.date_to) activeFilters.push({ label: 'To', value: filters.date_to, key: 'date_to' })

  return (
    <div>
      {/* Active Filter Chips */}
      {activeFilters.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {activeFilters.map(filter => (
            <FilterChip
              key={filter.key}
              label={filter.label}
              value={filter.value}
              onRemove={() => {
                if (filter.key === 'search') setFilters({ search: null })
                else if (filter.key === 'source') setFilters({ source: null })
                else if (filter.key === 'date_from') setFilters({ date_from: null })
                else if (filter.key === 'date_to') setFilters({ date_to: null })
                else if (filter.key.startsWith('severity-')) {
                  const severityToRemove = filter.key.split('-')[1]
                  const newSeverity = filters.severity?.filter(s => s !== severityToRemove)
                  setFilters({ severity: newSeverity?.length ? newSeverity : null })
                }
              }}
            />
          ))}
        </div>
      )}

      {/* Log Table with Loading Overlay */}
      <div className="relative">
        <LogTable
          logs={logs}
          onLoadMore={loadMore}
          hasMore={hasMore}
          isLoading={isLoading}
          sort={filters.sort || 'timestamp'}
          order={filters.order || 'desc'}
          onRefetch={refetch}
        />

        {/* Loading overlay - shown during filter updates */}
        {isLoading && logs.length > 0 && (
          <div className="absolute inset-0 bg-white/60 backdrop-blur-sm flex items-center justify-center rounded">
            <div className="bg-white px-6 py-3 rounded-lg shadow-lg border flex items-center gap-3">
              <div className="animate-spin h-5 w-5 border-2 border-slate-300 border-t-slate-600 rounded-full" />
              <span className="text-sm font-medium text-slate-700">Updating filters...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
