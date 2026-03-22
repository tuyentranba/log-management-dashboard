import { Severity } from './types'

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Severity badge colors - vibrant colors for better visual distinction
export const SEVERITY_COLORS = {
  INFO: 'border-transparent bg-blue-500 text-white hover:bg-blue-600',
  WARNING: 'border-transparent bg-yellow-500 text-white hover:bg-yellow-600',
  ERROR: 'border-transparent bg-orange-600 text-white hover:bg-orange-700',
  CRITICAL: 'border-transparent bg-red-600 text-white hover:bg-red-700',
} as const

export const SEVERITY_OPTIONS: Array<{value: Severity, label: string}> = [
  { value: 'INFO', label: 'INFO' },
  { value: 'WARNING', label: 'WARNING' },
  { value: 'ERROR', label: 'ERROR' },
  { value: 'CRITICAL', label: 'CRITICAL' },
]
