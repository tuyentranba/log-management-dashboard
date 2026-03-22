'use client'

import { useState } from 'react'
import { Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'
import { exportLogs } from '@/lib/api'
import { LogFilters } from '@/lib/types'

interface ExportButtonProps {
  filters: LogFilters
  disabled?: boolean  // Disable when no logs match filters
}

export function ExportButton({ filters, disabled }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = async () => {
    setIsExporting(true)

    try {
      await exportLogs(filters)
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
