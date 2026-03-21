import { Skeleton } from '@/components/ui/skeleton'

interface SkeletonRowsProps {
  count?: number
}

export function SkeletonRows({ count = 5 }: SkeletonRowsProps) {
  return (
    <div className="space-y-2">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 p-4 rounded animate-pulse" role="status" aria-label="Loading">
          <Skeleton className="w-20 h-6" /> {/* Severity badge */}
          <Skeleton className="flex-1 h-6" /> {/* Message */}
          <Skeleton className="w-32 h-6" /> {/* Timestamp */}
        </div>
      ))}
    </div>
  )
}
