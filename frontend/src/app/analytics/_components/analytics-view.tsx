'use client'

import { useState, useEffect } from 'react'
import { useQueryStates, parseAsString } from 'nuqs'
import { AnalyticsResponse } from '@/lib/types'
import { fetchAnalytics } from '@/lib/api'
import { SummaryStats } from './summary-stats'
import { TimeSeriesChart } from './time-series-chart'
import { SeverityDistributionChart } from './severity-distribution-chart'
import { TimeRangeFilter } from './time-range-filter'
import { Card } from '@/components/ui/card'

interface Props {
  initialData: AnalyticsResponse
}

export function AnalyticsView({ initialData }: Props) {
  const [data, setData] = useState<AnalyticsResponse>(initialData)
  const [isLoading, setIsLoading] = useState(false)

  // Read URL params for date range
  const [{ date_from, date_to }] = useQueryStates({
    date_from: parseAsString,
    date_to: parseAsString
  })

  // Refetch data when date range changes
  useEffect(() => {
    // Only refetch if URL params exist (user clicked a filter)
    // Skip if params are missing (initial load uses initialData)
    if (!date_from || !date_to) return

    console.log('[AnalyticsView] Refetching with:', { date_from, date_to })

    // Show loading immediately for better UX
    setIsLoading(true)

    // Add slight delay to batch rapid clicks
    const timeoutId = setTimeout(() => {
      const refetch = async () => {
        try {
          const newData = await fetchAnalytics({
            date_from,
            date_to
          })
          console.log('[AnalyticsView] Received data:', {
            total: newData.summary.total,
            timeSeriesPoints: newData.time_series.length
          })
          setData(newData)
        } catch (error) {
          console.error('[AnalyticsView] Failed to fetch analytics:', error)
        } finally {
          setIsLoading(false)
        }
      }

      refetch()
    }, 300) // 300ms debounce

    // Cleanup timeout on unmount or param change
    return () => {
      clearTimeout(timeoutId)
      setIsLoading(false)
    }
  }, [date_from, date_to])

  return (
    <div className="space-y-8">
      {/* Filter section */}
      <Card className="p-6">
        <TimeRangeFilter />
        {/* Future: Add severity and source dropdowns here */}
      </Card>

      {/* Data section with loading overlay */}
      <div className="relative space-y-8">
        {/* Loading overlay - matches log list style */}
        {isLoading && (
          <div className="absolute inset-0 bg-white/60 backdrop-blur-sm flex items-center justify-center rounded z-50">
            <div className="bg-white px-6 py-3 rounded-lg shadow-lg border flex items-center gap-3">
              <div className="animate-spin h-5 w-5 border-2 border-slate-300 border-t-slate-600 rounded-full" />
              <span className="text-sm font-medium text-slate-700">Updating charts...</span>
            </div>
          </div>
        )}

        {/* Summary stats cards */}
        <SummaryStats data={data.summary} />

        {/* Charts grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <TimeSeriesChart
            data={data.time_series}
            granularity={data.granularity}
          />
          <SeverityDistributionChart
            data={data.severity_distribution}
            total={data.summary.total}
          />
        </div>
      </div>
    </div>
  )
}
