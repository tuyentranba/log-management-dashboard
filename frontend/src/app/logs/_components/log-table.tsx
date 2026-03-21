'use client'

import { useVirtualizer } from '@tanstack/react-virtual'
import { useRef, useEffect } from 'react'
import { useQueryStates, parseAsString } from 'nuqs'
import { LogResponse } from '@/lib/types'
import { SeverityBadge } from '@/components/shared/severity-badge'
import { format } from 'date-fns'
import { ArrowUp, ArrowDown } from 'lucide-react'
import { LogDetailModal } from './log-detail-modal'

interface LogTableProps {
  logs: LogResponse[]
  onLoadMore: () => void
  hasMore: boolean
  isLoading: boolean
  sort: string
  order: string
}

export function LogTable({ logs, onLoadMore, hasMore, isLoading, sort, order }: LogTableProps) {
  const parentRef = useRef<HTMLDivElement>(null)
  const [, setSort] = useQueryStates({
    sort: parseAsString,
    order: parseAsString,
  })
  const [, setSelectedLogId] = useQueryStates({ log: parseAsString })

  const handleSort = (field: string) => {
    if (sort === field) {
      // Toggle order if same field
      setSort({ order: order === 'asc' ? 'desc' : 'asc' })
    } else {
      // New field, default to desc
      setSort({ sort: field, order: 'desc' })
    }
  }

  const SortIcon = ({ field }: { field: string }) => {
    if (sort !== field) return null
    return order === 'asc' ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />
  }

  const rowVirtualizer = useVirtualizer({
    count: logs.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 56, // Row height in pixels (per 03-UI-SPEC.md line 52)
    overscan: 5, // Render 5 extra rows above/below viewport
  })

  const virtualItems = rowVirtualizer.getVirtualItems()
  const lastItem = virtualItems[virtualItems.length - 1]

  // Trigger load more when scrolling near bottom
  useEffect(() => {
    if (lastItem && lastItem.index >= logs.length - 10 && hasMore && !isLoading) {
      onLoadMore()
    }
  }, [lastItem, hasMore, logs.length, onLoadMore, isLoading])

  return (
    <div className="border rounded">
      {/* Table Header */}
      <div className="flex items-center gap-4 p-4 bg-slate-50 border-b font-medium text-sm text-slate-700">
        <button
          onClick={() => handleSort('severity')}
          className="w-20 flex items-center gap-1 hover:text-slate-900 transition-colors"
        >
          Severity
          <SortIcon field="severity" />
        </button>
        <div className="flex-1">Message</div>
        <button
          onClick={() => handleSort('timestamp')}
          className="w-32 flex items-center justify-end gap-1 hover:text-slate-900 transition-colors"
        >
          Timestamp
          <SortIcon field="timestamp" />
        </button>
      </div>

      {/* Table Body with Virtual Scrolling */}
      <div ref={parentRef} className="h-[600px] overflow-auto">
        <div
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
            position: 'relative'
          }}
        >
          {virtualItems.map((virtualRow) => {
            const log = logs[virtualRow.index]
            return (
              <div
                key={virtualRow.key}
                className="flex items-center gap-4 p-4 hover:bg-slate-100 cursor-pointer border-b"
                onClick={() => setSelectedLogId({ log: log.id.toString() })}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: `${virtualRow.size}px`,
                  transform: `translateY(${virtualRow.start}px)`,
                }}
              >
                <div className="w-20">
                  <SeverityBadge severity={log.severity} />
                </div>
                <div className="flex-1 truncate">
                  {log.message}
                </div>
                <div className="w-32 text-sm text-slate-600 text-right">
                  {format(new Date(log.timestamp), 'MMM dd, HH:mm')}
                </div>
              </div>
            )
          })}
        </div>
      </div>
      <LogDetailModal />
    </div>
  )
}
