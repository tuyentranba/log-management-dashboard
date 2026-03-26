import { Suspense } from 'react'
import { AnalyticsView } from './_components/analytics-view'
import { fetchAnalytics } from '@/lib/api'
import { AnalyticsFilters } from '@/lib/types'
import { subDays } from 'date-fns'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export const dynamic = 'force-dynamic'  // Prevent build-time API calls

function AnalyticsLoadingSkeleton() {
  return (
    <div className="space-y-8">
      {/* Filter skeleton */}
      <Card className="p-6">
        <div className="flex gap-2">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="h-10 w-32" />
          ))}
        </div>
      </Card>

      {/* Stats skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <Card key={i} className="p-6">
            <Skeleton className="h-4 w-20 mb-2" />
            <Skeleton className="h-8 w-16" />
          </Card>
        ))}
      </div>

      {/* Charts skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <Skeleton className="h-6 w-48 mb-4" />
          <Skeleton className="h-[400px] w-full" />
        </Card>
        <Card className="p-6">
          <Skeleton className="h-6 w-48 mb-4" />
          <Skeleton className="h-[400px] w-full" />
        </Card>
      </div>
    </div>
  )
}

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

      <Suspense fallback={<AnalyticsLoadingSkeleton />}>
        <AnalyticsView initialData={initialData} />
      </Suspense>
    </div>
  )
}
