'use client'

import { useRef, Suspense } from 'react'
import { LogList } from './log-list'
import { ExportButton } from './export-button'
import { CreateButton } from './create-button'
import { CreateLogModal } from './create-log-modal'
import { SkeletonRows } from './skeleton-rows'
import { LogListResponse } from '@/lib/types'

interface LogsPageContentProps {
  initialData: LogListResponse
}

export function LogsPageContent({ initialData }: LogsPageContentProps) {
  const refetchRef = useRef<(() => void) | null>(null)

  const handleRefetch = (refetch: () => void) => {
    refetchRef.current = refetch
  }

  const triggerRefetch = () => {
    if (refetchRef.current) {
      refetchRef.current()
    }
  }

  return (
    <div className="flex-1 p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-semibold">Logs</h1>
        <div className="flex gap-2">
          <CreateButton />
          <ExportButton />
        </div>
      </div>

      <Suspense fallback={<SkeletonRows count={10} />}>
        {/* LogList reads filters directly from URL, only needs initial data */}
        <LogList initialData={initialData} onRefetch={handleRefetch} />
      </Suspense>

      {/* Create Log Modal */}
      <CreateLogModal onRefetch={triggerRefetch} />
    </div>
  )
}
