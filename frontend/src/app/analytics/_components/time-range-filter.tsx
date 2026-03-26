'use client'

import { useState, useEffect } from 'react'
import { useQueryStates, parseAsString } from 'nuqs'
import { subHours, subDays, format, isValid, parseISO } from 'date-fns'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { toast } from 'sonner'

const TIME_RANGES = [
  { label: 'Last hour', value: '1h', fn: () => subHours(new Date(), 1) },
  { label: 'Last 6 hours', value: '6h', fn: () => subHours(new Date(), 6) },
  { label: 'Last 24 hours', value: '24h', fn: () => subHours(new Date(), 24) },
  { label: 'Last 7 days', value: '7d', fn: () => subDays(new Date(), 7) },
  { label: 'Last 30 days', value: '30d', fn: () => subDays(new Date(), 30) },
  { label: 'Custom', value: 'custom', fn: null }
] as const

type TimeRangeValue = typeof TIME_RANGES[number]['value']

export function TimeRangeFilter() {
  const [{ date_from, date_to }, setQuery] = useQueryStates({
    date_from: parseAsString,
    date_to: parseAsString
  })

  const [selectedRange, setSelectedRange] = useState<TimeRangeValue>('7d')
  const [customFrom, setCustomFrom] = useState('')
  const [customTo, setCustomTo] = useState('')

  // Initialize custom date inputs from URL params on mount
  useEffect(() => {
    if (date_from && isValid(parseISO(date_from))) {
      setCustomFrom(format(parseISO(date_from), "yyyy-MM-dd'T'HH:mm"))
    }
    if (date_to && isValid(parseISO(date_to))) {
      setCustomTo(format(parseISO(date_to), "yyyy-MM-dd'T'HH:mm"))
    }
  }, [])

  // Sync selected range based on URL params
  useEffect(() => {
    if (!date_from || !date_to) {
      setSelectedRange('7d')
      return
    }

    const fromDate = parseISO(date_from)
    const toDate = parseISO(date_to)

    if (!isValid(fromDate) || !isValid(toDate)) {
      setSelectedRange('custom')
      return
    }

    // Check if URL dates match any preset
    const now = new Date()
    let matchedPreset = false

    for (const preset of TIME_RANGES) {
      if (preset.fn) {
        const presetFrom = preset.fn()
        const diffMs = Math.abs(fromDate.getTime() - presetFrom.getTime())
        const diffMinutes = diffMs / (1000 * 60)

        // Allow 5 minute tolerance for preset detection
        if (diffMinutes < 5) {
          setSelectedRange(preset.value)
          matchedPreset = true
          break
        }
      }
    }

    if (!matchedPreset) {
      setSelectedRange('custom')
    }
  }, [date_from, date_to])

  const handlePresetClick = (preset: typeof TIME_RANGES[number]) => {
    if (preset.value === 'custom') {
      setSelectedRange('custom')
      return
    }

    if (preset.fn) {
      const from = preset.fn()
      const to = new Date()

      console.log('[TimeRangeFilter] Setting query:', {
        preset: preset.value,
        date_from: from.toISOString(),
        date_to: to.toISOString()
      })

      setQuery({
        date_from: from.toISOString(),
        date_to: to.toISOString()
      })
      setSelectedRange(preset.value)
    }
  }

  const handleApplyCustom = () => {
    console.log('[TimeRangeFilter] Applying custom range:', { customFrom, customTo })

    if (!customFrom || !customTo) {
      toast.error('Please select both start and end dates')
      return
    }

    const fromDate = new Date(customFrom)
    const toDate = new Date(customTo)

    if (!isValid(fromDate) || !isValid(toDate)) {
      toast.error('Invalid date format')
      return
    }

    if (fromDate >= toDate) {
      toast.error('Start date must be before end date')
      return
    }

    console.log('[TimeRangeFilter] Setting custom query:', {
      date_from: fromDate.toISOString(),
      date_to: toDate.toISOString()
    })

    setQuery({
      date_from: fromDate.toISOString(),
      date_to: toDate.toISOString()
    })

    toast.success('Custom date range applied')
  }

  return (
    <div className="space-y-4">
      {/* Segmented button group */}
      <div className="flex flex-wrap gap-0">
        {TIME_RANGES.map((preset, index) => {
          const isFirst = index === 0
          const isLast = index === TIME_RANGES.length - 1
          const isSelected = selectedRange === preset.value

          let roundedClass = ''
          if (isFirst) {
            roundedClass = 'rounded-l-md'
          } else if (isLast) {
            roundedClass = 'rounded-r-md'
          }

          return (
            <Button
              key={preset.value}
              variant={isSelected ? 'default' : 'outline'}
              onClick={() => handlePresetClick(preset)}
              className={`${roundedClass} ${!isFirst ? '-ml-px' : ''} rounded-none first:rounded-l-md last:rounded-r-md`}
            >
              {preset.label}
            </Button>
          )
        })}
      </div>

      {/* Custom date picker section */}
      {selectedRange === 'custom' && (
        <Card className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="custom-from">From</Label>
              <Input
                id="custom-from"
                type="datetime-local"
                value={customFrom}
                onChange={(e) => setCustomFrom(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="custom-to">To</Label>
              <Input
                id="custom-to"
                type="datetime-local"
                value={customTo}
                onChange={(e) => setCustomTo(e.target.value)}
              />
            </div>
          </div>
          <div className="mt-4">
            <Button onClick={handleApplyCustom} className="w-full md:w-auto">
              Apply Custom Range
            </Button>
          </div>
        </Card>
      )}
    </div>
  )
}
