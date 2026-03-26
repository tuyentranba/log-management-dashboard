'use client'

import { useQueryState, parseAsBoolean } from 'nuqs'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { CreateForm } from './create-form'

export function CreateLogModal() {
  const [isCreating, setIsCreating] = useQueryState('create', parseAsBoolean)

  const handleCreateSuccess = () => {
    setIsCreating(false)  // Close modal - LogList auto-refreshes on URL change
  }

  return (
    <Dialog open={isCreating ?? false} onOpenChange={(open) => !open && setIsCreating(false)}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create Log</DialogTitle>
        </DialogHeader>
        <CreateForm onSuccess={handleCreateSuccess} />
      </DialogContent>
    </Dialog>
  )
}
