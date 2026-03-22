'use client'

import { LogListResponse } from '@/lib/types'
import { LogTable } from './log-table'
import { SkeletonRows } from './skeleton-rows'
import { FilterChip } from './filter-chip'
import { useInfiniteScroll } from '@/hooks/use-infinite-scroll'
import { useLogFilters } from '@/hooks/use-log-filters'

interface LogListProps {
  initialData: LogListResponse
}

export function LogList({ initialData }: LogListProps) {
  const [filters, setFilters] = useLogFilters()
  const { logs, hasMore, isLoading, loadMore } = useInfiniteScroll(initialData)

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

      {/* Log Table */}
      <LogTable
        logs={logs}
        onLoadMore={loadMore}
        hasMore={hasMore}
        isLoading={isLoading}
        sort={filters.sort || 'timestamp'}
        order={filters.order || 'desc'}
      />

      {isLoading && <SkeletonRows count={3} />}
    </div>
  )
}
