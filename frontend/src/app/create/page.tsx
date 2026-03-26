import { Suspense } from 'react'
import { CreateForm } from './_components/create-form'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

function CreateFormSkeleton() {
  return (
    <div className="space-y-6 max-w-2xl">
      {/* Timestamp field */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-10 w-full" />
      </div>

      {/* Message field */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-10 w-full" />
      </div>

      {/* Severity field */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-10 w-full" />
      </div>

      {/* Source field */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-10 w-full" />
      </div>

      {/* Submit button */}
      <Skeleton className="h-10 w-32" />
    </div>
  )
}

export default function CreateLogPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-6">Create Log</h1>
      <Suspense fallback={<CreateFormSkeleton />}>
        <CreateForm />
      </Suspense>
    </div>
  )
}
