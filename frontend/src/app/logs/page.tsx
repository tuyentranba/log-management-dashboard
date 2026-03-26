import { Suspense } from 'react'
import { LogsPageContent } from './_components/logs-page-content'
import { LogFilters as LogFiltersComponent } from './_components/log-filters'
import { SkeletonRows } from './_components/skeleton-rows'
import { fetchLogs } from '@/lib/api'
import { LogFilters, Severity } from '@/lib/types'

interface LogsPageProps {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}

export default async function LogsPage({ searchParams }: LogsPageProps) {
  const params = await searchParams

  // Parse URL search params into LogFilters for SSR initial data fetch
  const filters: LogFilters = {
    search: typeof params.search === 'string' ? params.search : undefined,
    severity: Array.isArray(params.severity)
      ? params.severity as Severity[]
      : typeof params.severity === 'string'
      ? params.severity.split(',') as Severity[]  // Split comma-separated string
      : undefined,
    source: typeof params.source === 'string' ? params.source : undefined,
    date_from: typeof params.date_from === 'string' ? params.date_from : undefined,
    date_to: typeof params.date_to === 'string' ? params.date_to : undefined,
    sort: (params.sort as any) || 'timestamp',
    order: (params.order as any) || 'desc',
  }

  // Fetch initial data on server with filters (SSR for performance)
  const initialData = await fetchLogs(filters, null, 50)

  return (
    <div className="flex">
      {/* Filter Sidebar */}
      <LogFiltersComponent />

      {/* Main Content - Client component handles refetch coordination */}
      <LogsPageContent initialData={initialData} />
    </div>
  )
}
