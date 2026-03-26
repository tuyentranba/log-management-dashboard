'use client'

import { useQueryState, parseAsBoolean } from 'nuqs'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'

export function CreateButton() {
  const [, setIsCreating] = useQueryState('create', parseAsBoolean)

  return (
    <Button onClick={() => setIsCreating(true)}>
      <Plus className="h-4 w-4 mr-2" />
      Create Log
    </Button>
  )
}
