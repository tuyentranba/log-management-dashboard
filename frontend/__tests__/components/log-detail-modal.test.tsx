import { render, screen, waitFor } from '../utils/test-utils'
import userEvent from '@testing-library/user-event'
import { axe } from 'jest-axe'
import { LogDetailModal } from '@/app/logs/_components/log-detail-modal'
import * as api from '@/lib/api'

jest.mock('@/lib/api')
jest.mock('nuqs', () => ({
  useQueryState: jest.fn(() => [null, jest.fn()]),
}))

const mockLog = {
  id: 1,
  timestamp: '2024-01-15T10:30:00Z',
  message: 'Test log message',
  severity: 'INFO' as const,
  source: 'test-service'
}

describe('LogDetailModal', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('does not render when log ID is null', () => {
    const { useQueryState } = require('nuqs')
    useQueryState.mockReturnValue([null, jest.fn()])

    render(<LogDetailModal onRefetch={jest.fn()} />)

    expect(screen.queryByText('Log Details')).not.toBeInTheDocument()
  })

  it('fetches and displays log details when ID is provided', async () => {
    const { useQueryState } = require('nuqs')
    useQueryState.mockReturnValue(['1', jest.fn()])
    jest.spyOn(api, 'fetchLogById').mockResolvedValue(mockLog)

    render(<LogDetailModal onRefetch={jest.fn()} />)

    await waitFor(() => {
      expect(screen.getByText('Test log message')).toBeInTheDocument()
      expect(screen.getByText(/INFO/i)).toBeInTheDocument()
      expect(screen.getByText('test-service')).toBeInTheDocument()
    })
  })

  it('shows Edit and Delete buttons in view mode', async () => {
    const { useQueryState } = require('nuqs')
    useQueryState.mockReturnValue(['1', jest.fn()])
    jest.spyOn(api, 'fetchLogById').mockResolvedValue(mockLog)

    render(<LogDetailModal onRefetch={jest.fn()} />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
    })
  })

  it('switches to edit mode when Edit button clicked', async () => {
    const { useQueryState } = require('nuqs')
    useQueryState.mockReturnValue(['1', jest.fn()])
    jest.spyOn(api, 'fetchLogById').mockResolvedValue(mockLog)
    const user = userEvent.setup()

    render(<LogDetailModal onRefetch={jest.fn()} />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument()
    })

    await user.click(screen.getByRole('button', { name: /edit/i }))

    // Edit form should appear with pre-filled message field
    expect(screen.getByLabelText(/message/i)).toHaveValue('Test log message')
  })

  it('calls onRefetch after successful update', async () => {
    const { useQueryState } = require('nuqs')
    const mockSetSelectedLogId = jest.fn()
    useQueryState.mockReturnValue(['1', mockSetSelectedLogId])
    jest.spyOn(api, 'fetchLogById').mockResolvedValue(mockLog)
    jest.spyOn(api, 'updateLog').mockResolvedValue({ ...mockLog, message: 'Updated' })
    const mockOnRefetch = jest.fn()
    const user = userEvent.setup()

    render(<LogDetailModal onRefetch={mockOnRefetch} />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument()
    })

    await user.click(screen.getByRole('button', { name: /edit/i }))

    const messageInput = screen.getByLabelText(/message/i)
    await user.clear(messageInput)
    await user.type(messageInput, 'Updated')
    await user.click(screen.getByRole('button', { name: /save|update/i }))

    await waitFor(() => {
      expect(mockOnRefetch).toHaveBeenCalled()
      expect(mockSetSelectedLogId).toHaveBeenCalledWith(null)
    })
  })

  it('shows confirmation dialog before delete', async () => {
    const { useQueryState } = require('nuqs')
    useQueryState.mockReturnValue(['1', jest.fn()])
    jest.spyOn(api, 'fetchLogById').mockResolvedValue(mockLog)
    global.confirm = jest.fn(() => false)
    const user = userEvent.setup()

    render(<LogDetailModal onRefetch={jest.fn()} />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
    })

    await user.click(screen.getByRole('button', { name: /delete/i }))

    expect(global.confirm).toHaveBeenCalledWith(expect.stringContaining('Delete log 1?'))
  })

  it('has no accessibility violations', async () => {
    const { useQueryState } = require('nuqs')
    useQueryState.mockReturnValue(['1', jest.fn()])
    jest.spyOn(api, 'fetchLogById').mockResolvedValue(mockLog)

    const { container } = render(<LogDetailModal onRefetch={jest.fn()} />)

    await waitFor(() => {
      expect(screen.getByText('Test log message')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
