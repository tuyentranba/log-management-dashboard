'use client'

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { format, parseISO } from 'date-fns'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface TimeSeriesDataPoint {
  timestamp: string
  count: number
}

interface Props {
  data: TimeSeriesDataPoint[]
  granularity: 'hour' | 'day' | 'week'
}

export function TimeSeriesChart({ data, granularity }: Props) {
  // Format X-axis based on granularity
  const formatXAxis = (timestamp: string) => {
    const date = parseISO(timestamp)
    if (granularity === 'hour') {
      return format(date, 'MMM d, HH:mm')  // "Mar 25, 14:00"
    } else if (granularity === 'day') {
      return format(date, 'MMM d')  // "Mar 25"
    } else {
      return format(date, 'MMM d')  // "Mar 25" (week start)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Log Volume Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={formatXAxis}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis />
            <Tooltip
              labelFormatter={(value) => format(parseISO(value as string), 'PPpp')}
              formatter={(value: number) => [`${value} logs`, 'Count']}
            />
            <Area
              type="monotone"
              dataKey="count"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.6}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
