'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'next/navigation'
import { z } from 'zod'
import { LogCreate, Severity } from '@/lib/types'
import { SEVERITY_OPTIONS } from '@/lib/constants'
import { createLog } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'

// Zod schema matching backend Pydantic validation
const logCreateSchema = z.object({
  timestamp: z.string().datetime({ message: 'Must be ISO 8601 format with timezone' }),
  message: z.string().min(1, 'Message is required'),
  severity: z.enum(['INFO', 'WARNING', 'ERROR', 'CRITICAL'], {
    message: 'Must be INFO, WARNING, ERROR, or CRITICAL',
  }),
  source: z.string().min(1, 'Source is required').max(100, 'Source must be ≤100 characters'),
})

export function CreateForm() {
  const router = useRouter()
  const form = useForm<LogCreate>({
    resolver: zodResolver(logCreateSchema),
    defaultValues: {
      timestamp: new Date().toISOString(),
      message: '',
      severity: 'INFO' as Severity,
      source: '',
    },
  })

  const onSubmit = async (data: LogCreate) => {
    try {
      await createLog(data)
      toast.success('Log created successfully')
      router.push('/logs')
    } catch (error) {
      toast.error('Failed to create log. Please try again.')
      console.error('Create log error:', error)
    }
  }

  const isSubmitting = form.formState.isSubmitting

  return (
    <div className="relative">
      {/* Submission overlay - matches analytics loading style */}
      {isSubmitting && (
        <div className="absolute inset-0 bg-white/60 backdrop-blur-sm flex items-center justify-center rounded z-50">
          <div className="bg-white px-6 py-3 rounded-lg shadow-lg border flex items-center gap-3">
            <div className="animate-spin h-5 w-5 border-2 border-slate-300 border-t-slate-600 rounded-full" />
            <span className="text-sm font-medium text-slate-700">Creating log...</span>
          </div>
        </div>
      )}

      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 max-w-2xl">
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

        {/* Submit Button */}
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isSubmitting ? 'Creating...' : 'Create Log'}
        </Button>
      </form>
    </div>
  )
}
