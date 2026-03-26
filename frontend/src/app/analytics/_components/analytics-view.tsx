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

    const refetch = async () => {
      setIsLoading(true)
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
  }, [date_from, date_to])

  return (
    <div className="space-y-8">
      {/* Filter section */}
      <Card className="p-6">
        <TimeRangeFilter />
        {/* Future: Add severity and source dropdowns here */}
      </Card>

      {/* Loading overlay */}
      {isLoading && (
        <div className="relative">
          <div className="absolute inset-0 bg-background/50 backdrop-blur-sm z-10 flex items-center justify-center">
            <div className="flex flex-col items-center gap-2">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="text-sm text-muted-foreground">Updating charts...</p>
            </div>
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
  )
}
