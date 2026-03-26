'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { LogCreate, LogResponse, Severity } from '@/lib/types'
import { SEVERITY_OPTIONS } from '@/lib/constants'
import { updateLog } from '@/lib/api'
import { toDatetimeLocalString } from '@/lib/date-utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'

// Reuse same Zod schema as CreateForm (matches backend Pydantic validation)
const logCreateSchema = z.object({
  timestamp: z.string().datetime({ message: 'Must be ISO 8601 format with timezone' }),
  message: z.string().min(1, 'Message is required'),
  severity: z.enum(['INFO', 'WARNING', 'ERROR', 'CRITICAL'], {
    message: 'Must be INFO, WARNING, ERROR, or CRITICAL',
  }),
  source: z.string().min(1, 'Source is required').max(100, 'Source must be ≤100 characters'),
})

interface EditFormProps {
  log: LogResponse
  onSuccess: () => void
  onCancel: () => void
}

export function EditForm({ log, onSuccess, onCancel }: EditFormProps) {
  const form = useForm<LogCreate>({
    resolver: zodResolver(logCreateSchema),
    defaultValues: {
      timestamp: toDatetimeLocalString(new Date(log.timestamp)),
      message: log.message,
      severity: log.severity,
      source: log.source,
    },
  })

  const onSubmit = async (data: LogCreate) => {
    try {
      await updateLog(log.id, data)
      toast.success('Log updated successfully')
      onSuccess()
    } catch (error) {
      toast.error('Failed to update log. Please try again.')
      console.error('Update log error:', error)
    }
  }

  const isSubmitting = form.formState.isSubmitting

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      {/* Timestamp Field */}
      <div className="space-y-2">
        <Label htmlFor="timestamp">Timestamp</Label>
        <Input
          id="timestamp"
          type="datetime-local"
          step="1"
          {...form.register('timestamp', {
            setValueAs: (value) => {
              // Convert datetime-local to ISO 8601 with timezone
              if (!value) return ''
              const date = new Date(value)
              return date.toISOString()
            },
          })}
          disabled={isSubmitting}
        />
        {form.formState.errors.timestamp && (
          <p className="text-sm text-red-600">{form.formState.errors.timestamp.message}</p>
        )}
      </div>

      {/* Message Field */}
      <div className="space-y-2">
        <Label htmlFor="message">Message</Label>
        <Input
          id="message"
          {...form.register('message')}
          placeholder="Enter log message"
          disabled={isSubmitting}
        />
        {form.formState.errors.message && (
          <p className="text-sm text-red-600">{form.formState.errors.message.message}</p>
        )}
      </div>

      {/* Severity Field */}
      <div className="space-y-2">
        <Label htmlFor="severity">Severity</Label>
        <Select
          value={form.watch('severity')}
          onValueChange={(value) => form.setValue('severity', value as Severity)}
          disabled={isSubmitting}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {SEVERITY_OPTIONS.map(option => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {form.formState.errors.severity && (
          <p className="text-sm text-red-600">{form.formState.errors.severity.message}</p>
        )}
      </div>

      {/* Source Field */}
      <div className="space-y-2">
        <Label htmlFor="source">Source</Label>
        <Input
          id="source"
          {...form.register('source')}
          placeholder="e.g., api-service"
          disabled={isSubmitting}
        />
        {form.formState.errors.source && (
          <p className="text-sm text-red-600">{form.formState.errors.source.message}</p>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2 pt-2">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isSubmitting ? 'Saving...' : 'Save Changes'}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </Button>
      </div>
    </form>
  )
}
