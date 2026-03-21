'use client'

import { useQueryStates, parseAsString, parseAsArrayOf } from 'nuqs'
import { SearchInput } from './search-input'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { SEVERITY_OPTIONS } from '@/lib/constants'

export function LogFilters() {
  const [filters, setFilters] = useQueryStates({
    search: parseAsString,
    severity: parseAsArrayOf(parseAsString),
    source: parseAsString,
    date_from: parseAsString,
    date_to: parseAsString,
    sort: parseAsString.withDefault('timestamp'),
    order: parseAsString.withDefault('desc'),
  })

  const handleSeverityToggle = (value: string) => {
    const currentSeverity = filters.severity || []
    const newSeverity = currentSeverity.includes(value)
      ? currentSeverity.filter(s => s !== value)
      : [...currentSeverity, value]
    setFilters({ severity: newSeverity.length > 0 ? newSeverity : null })
  }

  const clearFilters = () => {
    setFilters({
      search: null,
      severity: null,
      source: null,
      date_from: null,
      date_to: null,
      sort: 'timestamp',
      order: 'desc',
    })
  }

  const hasActiveFilters = Boolean(
    filters.search || filters.severity?.length || filters.source || filters.date_from || filters.date_to
  )

  return (
    <div className="w-64 border-r p-4 space-y-6">
      <div>
        <h2 className="text-lg font-semibold mb-4">Filters</h2>

        {/* Search Input */}
        <div className="space-y-2">
          <Label>Search</Label>
          <SearchInput />
        </div>

        {/* Date Range */}
        <div className="space-y-2 mt-4">
          <Label>Start Date</Label>
          <Input
            type="date"
            value={filters.date_from || ''}
            onChange={(e) => setFilters({ date_from: e.target.value || null })}
          />
        </div>

        <div className="space-y-2 mt-4">
          <Label>End Date</Label>
          <Input
            type="date"
            value={filters.date_to || ''}
            onChange={(e) => setFilters({ date_to: e.target.value || null })}
          />
        </div>

        {/* Severity Filter */}
        <div className="space-y-2 mt-4">
          <Label>Severity</Label>
          <div className="space-y-2">
            {SEVERITY_OPTIONS.map(option => (
              <label key={option.value} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.severity?.includes(option.value) || false}
                  onChange={() => handleSeverityToggle(option.value)}
                  className="rounded"
                />
                <span className="text-sm">{option.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Source Filter */}
        <div className="space-y-2 mt-4">
          <Label>Source</Label>
          <Input
            type="text"
            value={filters.source || ''}
            onChange={(e) => setFilters({ source: e.target.value || null })}
            placeholder="e.g., api-service"
          />
        </div>

        <Separator className="my-4" />

        {/* Reset Button */}
        {hasActiveFilters && (
          <Button
            variant="outline"
            className="w-full"
            onClick={clearFilters}
          >
            Reset Filters
          </Button>
        )}
      </div>
    </div>
  )
}
