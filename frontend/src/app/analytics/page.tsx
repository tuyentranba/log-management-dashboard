import { Suspense } from 'react'
import { AnalyticsView } from './_components/analytics-view'
import { fetchAnalytics } from '@/lib/api'
import { AnalyticsFilters } from '@/lib/types'
import { subDays } from 'date-fns'

export const dynamic = 'force-dynamic'  // Prevent build-time API calls

interface AnalyticsPageProps {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}

export default async function AnalyticsPage({ searchParams }: AnalyticsPageProps) {
  const params = await searchParams

  // Default to last 7 days if no date range provided
  const defaultDateFrom = subDays(new Date(), 7).toISOString()
  const defaultDateTo = new Date().toISOString()

  // Build filters from URL params
  const filters: AnalyticsFilters = {
    date_from: (params.date_from as string) || defaultDateFrom,
    date_to: (params.date_to as string) || defaultDateTo,
    severity: params.severity ? (Array.isArray(params.severity) ? params.severity : [params.severity]) as any : undefined,
    source: params.source as string | undefined,
  }

  // Fetch initial data on server
  const initialData = await fetchAnalytics(filters)

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
        <a
          href="/logs"
          className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
        >
          View All Logs
        </a>
      </div>

      <Suspense fallback={<div>Loading...</div>}>
        <AnalyticsView initialData={initialData} />
      </Suspense>
    </div>
  )
}
