'use client'

import { useState } from 'react'
import { Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'
import { exportLogs } from '@/lib/api'
import { useLogFilters } from '@/hooks/use-log-filters'
import { LogFilters } from '@/lib/types'

interface ExportButtonProps {
  disabled?: boolean  // Disable when no logs match filters
}

export function ExportButton({ disabled }: ExportButtonProps) {
  const [filters] = useLogFilters()  // Get real-time filters from URL state
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = async () => {
    setIsExporting(true)

    try {
      // Convert null values to undefined and cast types for API compatibility
      const exportFilters: LogFilters = {
        search: filters.search ?? undefined,
        severity: (filters.severity as LogFilters['severity']) ?? undefined,
        source: filters.source ?? undefined,
        date_from: filters.date_from ?? undefined,
        date_to: filters.date_to ?? undefined,
        sort: (filters.sort as LogFilters['sort']) ?? 'timestamp',
        order: (filters.order as LogFilters['order']) ?? 'desc',
      }
      await exportLogs(exportFilters)
      toast.success('CSV exported successfully', {
        description: 'Your file has been downloaded'
      })
    } catch (error) {
      toast.error('Export failed', {
        description: error instanceof Error ? error.message : 'Unknown error'
      })
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <Button
      onClick={handleExport}
      disabled={disabled || isExporting}
      variant="outline"
    >
      <Download className="mr-2 h-4 w-4" />
      {isExporting ? 'Exporting...' : 'Export CSV'}
    </Button>
  )
}
