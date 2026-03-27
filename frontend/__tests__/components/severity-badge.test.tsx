import { render, screen } from '../utils/test-utils'
import { SeverityBadge } from '@/components/shared/severity-badge'

describe('SeverityBadge', () => {
  it('renders INFO severity with blue background', () => {
    render(<SeverityBadge severity="INFO" />)
    const badge = screen.getByText('INFO')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-blue-500')
  })

  it('renders WARNING severity with yellow background', () => {
    render(<SeverityBadge severity="WARNING" />)
    const badge = screen.getByText('WARNING')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-yellow-500')
  })

  it('renders ERROR severity with orange background', () => {
    render(<SeverityBadge severity="ERROR" />)
    const badge = screen.getByText('ERROR')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-orange-600')
  })

  it('renders CRITICAL severity with red background', () => {
    render(<SeverityBadge severity="CRITICAL" />)
    const badge = screen.getByText('CRITICAL')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-red-600')
  })

  it('applies white text color to all severities', () => {
    render(<SeverityBadge severity="INFO" />)
    const badge = screen.getByText('INFO')
    expect(badge).toHaveClass('text-white')
  })
})
