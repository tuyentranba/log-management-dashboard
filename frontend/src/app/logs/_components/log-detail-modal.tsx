'use client'

import { useEffect, useState } from 'react'
import { useQueryState } from 'nuqs'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { SeverityBadge } from '@/components/shared/severity-badge'
import { fetchLogById } from '@/lib/api'
import { LogResponse } from '@/lib/types'
import { format } from 'date-fns'
import { toast } from 'sonner'

export function LogDetailModal() {
  const [selectedLogId, setSelectedLogId] = useQueryState('log')
  const [log, setLog] = useState<LogResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (!selectedLogId) {
      setLog(null)
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

  const isOpen = Boolean(selectedLogId)

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && setSelectedLogId(null)}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Log Details</DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div className="py-8 text-center text-slate-600">Loading...</div>
        ) : log ? (
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
        ) : null}
      </DialogContent>
    </Dialog>
  )
}
