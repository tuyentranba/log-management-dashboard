'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface SeverityDataPoint {
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
  count: number
}

interface Props {
  data: SeverityDataPoint[]
  total: number
}

const SEVERITY_CHART_COLORS = {
  INFO: '#3b82f6',      // blue-500
  WARNING: '#eab308',   // yellow-500
  ERROR: '#ea580c',     // orange-600
  CRITICAL: '#dc2626',  // red-600
}

export function SeverityDistributionChart({ data, total }: Props) {
  const router = useRouter()

  const handleBarClick = (dataPoint: SeverityDataPoint) => {
    // Navigate to /logs with severity pre-selected
    router.push(`/logs?severity=${dataPoint.severity}`)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Logs by Severity</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="severity" />
            <YAxis />
            <Tooltip
              formatter={(value: number, name, props) => {
                const percentage = ((value / total) * 100).toFixed(1)
                return [`${value} logs (${percentage}%)`, 'Count']
              }}
            />
            <Bar
              dataKey="count"
              onClick={handleBarClick}
              cursor="pointer"
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={SEVERITY_CHART_COLORS[entry.severity] || '#6b7280'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
