import { render, screen, waitFor } from '../utils/test-utils'
import userEvent from '@testing-library/user-event'
import { axe } from 'jest-axe'
import { EditForm } from '@/app/logs/_components/edit-form'
import * as api from '@/lib/api'

jest.mock('@/lib/api')

const mockLog = {
  id: 1,
  timestamp: '2024-01-15T10:30:00Z',
  message: 'Original message',
  severity: 'INFO' as const,
  source: 'original-source'
}

describe('EditForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('pre-populates fields with log data', () => {
    render(<EditForm log={mockLog} onSuccess={jest.fn()} onCancel={jest.fn()} />)

    expect(screen.getByLabelText(/message/i)).toHaveValue('Original message')
    expect(screen.getByLabelText(/severity/i)).toHaveTextContent('INFO')
    expect(screen.getByLabelText(/source/i)).toHaveValue('original-source')
  })

  it('shows validation error for empty message', async () => {
    const user = userEvent.setup()
    render(<EditForm log={mockLog} onSuccess={jest.fn()} onCancel={jest.fn()} />)

    const messageInput = screen.getByLabelText(/message/i)
    await user.clear(messageInput)
    await user.click(screen.getByRole('button', { name: /save|update/i }))

    expect(await screen.findByText(/message.*required/i)).toBeInTheDocument()
  })

  it('submits updated data', async () => {
    const user = userEvent.setup()
    const mockOnSuccess = jest.fn()
    const mockUpdateLog = jest.spyOn(api, 'updateLog').mockResolvedValue({
      ...mockLog,
      message: 'Updated message'
    })

    render(<EditForm log={mockLog} onSuccess={mockOnSuccess} onCancel={jest.fn()} />)

    const messageInput = screen.getByLabelText(/message/i)
    await user.clear(messageInput)
    await user.type(messageInput, 'Updated message')
    await user.click(screen.getByRole('button', { name: /save|update/i }))

    await waitFor(() => {
      expect(mockUpdateLog).toHaveBeenCalledWith(
        1,
        expect.objectContaining({
          message: 'Updated message',
        })
      )
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })

  it('calls onCancel when cancel button clicked', async () => {
    const user = userEvent.setup()
    const mockOnCancel = jest.fn()

    render(<EditForm log={mockLog} onSuccess={jest.fn()} onCancel={mockOnCancel} />)

    await user.click(screen.getByRole('button', { name: /cancel/i }))

    expect(mockOnCancel).toHaveBeenCalled()
  })

  it('disables buttons during submission', async () => {
    const user = userEvent.setup()
    jest.spyOn(api, 'updateLog').mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    render(<EditForm log={mockLog} onSuccess={jest.fn()} onCancel={jest.fn()} />)

    const saveButton = screen.getByRole('button', { name: /save|update/i })
    await user.click(saveButton)

    expect(saveButton).toBeDisabled()
    expect(screen.getByRole('button', { name: /cancel/i })).toBeDisabled()
  })

  it('has no accessibility violations', async () => {
    const { container } = render(<EditForm log={mockLog} onSuccess={jest.fn()} onCancel={jest.fn()} />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
