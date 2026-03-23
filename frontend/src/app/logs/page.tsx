import { Suspense } from 'react'
import { LogList } from './_components/log-list'
import { LogFilters as LogFiltersComponent } from './_components/log-filters'
import { SkeletonRows } from './_components/skeleton-rows'
import { ExportButton } from './_components/export-button'
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

      {/* Main Content */}
      <div className="flex-1 p-6">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-semibold">Logs</h1>
          <ExportButton />
        </div>

        <Suspense fallback={<SkeletonRows count={10} />}>
          {/* LogList reads filters directly from URL, only needs initial data */}
          <LogList initialData={initialData} />
        </Suspense>
      </div>
    </div>
  )
}
