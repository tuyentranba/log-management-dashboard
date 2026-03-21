import { Severity } from './types'

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Severity badge colors per 03-UI-SPEC.md lines 85-89
export const SEVERITY_COLORS = {
  INFO: 'bg-blue-100 text-blue-800',
  WARNING: 'bg-yellow-100 text-yellow-800',
  ERROR: 'bg-red-100 text-red-800',
  CRITICAL: 'bg-red-900 text-white',
} as const

export const SEVERITY_OPTIONS: Array<{value: Severity, label: string}> = [
  { value: 'INFO', label: 'INFO' },
  { value: 'WARNING', label: 'WARNING' },
  { value: 'ERROR', label: 'ERROR' },
  { value: 'CRITICAL', label: 'CRITICAL' },
]
