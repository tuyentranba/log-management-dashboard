'use client'

import { X } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

interface FilterChipProps {
  label: string
  value: string
  onRemove: () => void
}

export function FilterChip({ label, value, onRemove }: FilterChipProps) {
  return (
    <Badge variant="secondary" className="flex items-center gap-1 pr-1">
      <span className="text-xs">{label}: {value}</span>
      <Button
        variant="ghost"
        size="sm"
        className="h-4 w-4 p-0 hover:bg-slate-200"
        onClick={onRemove}
        aria-label={`Remove ${label} filter`}
      >
        <X className="h-3 w-3" />
      </Button>
    </Badge>
  )
}
