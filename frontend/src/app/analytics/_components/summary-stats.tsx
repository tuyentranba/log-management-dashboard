import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Props {
  data: {
    total: number
    by_severity: {
      INFO: number
      WARNING: number
      ERROR: number
      CRITICAL: number
    }
  }
}

export function SummaryStats({ data }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
      {/* Total logs card */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">Total Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{data.total.toLocaleString()}</div>
        </CardContent>
      </Card>

      {/* INFO card with blue tint */}
      <Card className="bg-blue-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-blue-700">INFO</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-blue-700">
            {data.by_severity.INFO.toLocaleString()}
          </div>
        </CardContent>
      </Card>

      {/* WARNING card with yellow tint */}
      <Card className="bg-yellow-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-yellow-700">WARNING</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-yellow-700">
            {data.by_severity.WARNING.toLocaleString()}
          </div>
        </CardContent>
      </Card>

      {/* ERROR card with orange tint */}
      <Card className="bg-orange-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-orange-700">ERROR</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-orange-700">
            {data.by_severity.ERROR.toLocaleString()}
          </div>
        </CardContent>
      </Card>

      {/* CRITICAL card with red tint */}
      <Card className="bg-red-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-red-700">CRITICAL</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-red-700">
            {data.by_severity.CRITICAL.toLocaleString()}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
