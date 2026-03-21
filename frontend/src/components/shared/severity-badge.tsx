import { Severity } from '@/lib/types'
import { SEVERITY_COLORS } from '@/lib/constants'
import { Badge } from '@/components/ui/badge'

interface SeverityBadgeProps {
  severity: Severity
}

export function SeverityBadge({ severity }: SeverityBadgeProps) {
  const colorClass = SEVERITY_COLORS[severity]

  return (
    <Badge className={colorClass}>
      {severity}
    </Badge>
  )
}
