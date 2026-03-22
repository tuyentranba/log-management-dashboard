import { Severity } from './types'

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Severity badge colors - semantic names using CSS variables
export const SEVERITY_COLORS = {
  INFO: 'border-transparent bg-severity-info text-white hover:bg-severity-info/90',
  WARNING: 'border-transparent bg-severity-warning text-white hover:bg-severity-warning/90',
  ERROR: 'border-transparent bg-severity-error text-white hover:bg-severity-error/90',
  CRITICAL: 'border-transparent bg-severity-critical text-white hover:bg-severity-critical/90',
} as const

export const SEVERITY_OPTIONS: Array<{value: Severity, label: string}> = [
  { value: 'INFO', label: 'INFO' },
  { value: 'WARNING', label: 'WARNING' },
  { value: 'ERROR', label: 'ERROR' },
  { value: 'CRITICAL', label: 'CRITICAL' },
]
