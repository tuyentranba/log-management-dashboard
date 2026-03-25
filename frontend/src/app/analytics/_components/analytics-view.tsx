'use client'

import { AnalyticsResponse } from '@/lib/types'
import { SummaryStats } from './summary-stats'
import { TimeSeriesChart } from './time-series-chart'
import { SeverityDistributionChart } from './severity-distribution-chart'
import { TimeRangeFilter } from './time-range-filter'
import { Card } from '@/components/ui/card'

interface Props {
  initialData: AnalyticsResponse
}

export function AnalyticsView({ initialData }: Props) {
  // For Phase 5, we'll use initialData directly
  // Future enhancement: add client-side filter state and refetching

  return (
    <div className="space-y-8">
      {/* Filter section */}
      <Card className="p-6">
        <TimeRangeFilter />
        {/* Future: Add severity and source dropdowns here */}
      </Card>

      {/* Summary stats cards */}
      <SummaryStats data={initialData.summary} />

      {/* Charts grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <TimeSeriesChart
          data={initialData.time_series}
          granularity={initialData.granularity}
        />
        <SeverityDistributionChart
          data={initialData.severity_distribution}
          total={initialData.summary.total}
        />
      </div>
    </div>
  )
}
