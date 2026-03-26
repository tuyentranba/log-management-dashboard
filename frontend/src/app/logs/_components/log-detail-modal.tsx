'use client'

import { useEffect, useState } from 'react'
import { useQueryState } from 'nuqs'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { SeverityBadge } from '@/components/shared/severity-badge'
import { EditForm } from './edit-form'
import { fetchLogById, deleteLog } from '@/lib/api'
import { LogResponse } from '@/lib/types'
import { format } from 'date-fns'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'

export function LogDetailModal() {
  const [selectedLogId, setSelectedLogId] = useQueryState('log')
  const [log, setLog] = useState<LogResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [mode, setMode] = useState<'view' | 'edit'>('view')
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    if (!selectedLogId) {
      setLog(null)
      setMode('view')  // Reset mode when modal closes
      return
    }

    const loadLog = async () => {
      setIsLoading(true)
      try {
        const data = await fetchLogById(parseInt(selectedLogId))
        setLog(data)
      } catch (error) {
        toast.error('Failed to load log details')
        setSelectedLogId(null)
      } finally {
        setIsLoading(false)
      }
    }

    loadLog()
  }, [selectedLogId, setSelectedLogId])

  const handleEditClick = () => {
    setMode('edit')
  }

  const handleCancelEdit = () => {
    setMode('view')
  }

  const handleUpdateSuccess = () => {
    toast.success('Log updated successfully')
    setSelectedLogId(null)  // Close modal, triggers list refresh
  }

  const handleDeleteClick = async () => {
    if (!log) return

    // Confirmation dialog with log details
    const message = `Delete log ${log.id}?\n\nTimestamp: ${format(new Date(log.timestamp), 'PPpp')}\nSeverity: ${log.severity}\nSource: ${log.source}\nMessage: ${log.message.slice(0, 100)}${log.message.length > 100 ? '...' : ''}`

    if (!confirm(message)) {
      return
    }

    setIsDeleting(true)
    try {
      await deleteLog(log.id)
      toast.success('Log deleted successfully')
      setSelectedLogId(null)  // Close modal, triggers list refresh
    } catch (error) {
      toast.error('Failed to delete log. Please try again.')
      console.error('Delete log error:', error)
    } finally {
      setIsDeleting(false)
    }
  }

  const isOpen = Boolean(selectedLogId)

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && setSelectedLogId(null)}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{mode === 'view' ? 'Log Details' : 'Edit Log'}</DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div className="py-8 text-center text-slate-600">Loading...</div>
        ) : log ? (
          <>
            {mode === 'view' ? (
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-slate-700">ID</label>
                  <div className="text-sm text-slate-900">{log.id}</div>
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-700">Timestamp</label>
                  <div className="text-sm text-slate-900">
                    {format(new Date(log.timestamp), 'PPpp')}
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-700">Severity</label>
                  <div className="mt-1">
                    <SeverityBadge severity={log.severity} />
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-700">Source</label>
                  <div className="text-sm text-slate-900">{log.source}</div>
                </div>

                <div>
                  <label className="text-sm font-medium text-slate-700">Message</label>
                  <div className="text-sm text-slate-900 whitespace-pre-wrap">{log.message}</div>
                </div>
              </div>
            ) : (
              <EditForm log={log} onSuccess={handleUpdateSuccess} onCancel={handleCancelEdit} />
            )}

            {mode === 'view' && (
              <DialogFooter className="gap-2">
                <Button onClick={handleEditClick} disabled={isDeleting}>
                  Edit
                </Button>
                <Button variant="destructive" onClick={handleDeleteClick} disabled={isDeleting}>
                  {isDeleting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {isDeleting ? 'Deleting...' : 'Delete'}
                </Button>
              </DialogFooter>
            )}
          </>
        ) : null}
      </DialogContent>
    </Dialog>
  )
}
