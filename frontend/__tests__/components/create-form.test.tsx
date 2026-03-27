import { render, screen, waitFor } from '../utils/test-utils'
import userEvent from '@testing-library/user-event'
import { axe } from 'jest-axe'
import { CreateForm } from '@/app/logs/_components/create-form'
import * as api from '@/lib/api'

jest.mock('@/lib/api')
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))

describe('CreateForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders all form fields', () => {
    render(<CreateForm />)
    expect(screen.getByLabelText(/timestamp/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/severity/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/source/i)).toBeInTheDocument()
  })

  it('shows validation error for empty message', async () => {
    const user = userEvent.setup()
    render(<CreateForm />)

    // Clear the message field and submit
    const messageInput = screen.getByLabelText(/message/i)
    await user.clear(messageInput)
    await user.click(screen.getByRole('button', { name: /create log/i }))

    expect(await screen.findByText(/message.*required/i)).toBeInTheDocument()
  })

  it('shows validation error for empty source', async () => {
    const user = userEvent.setup()
    render(<CreateForm />)

    // Clear the source field and submit
    const sourceInput = screen.getByLabelText(/source/i)
    await user.clear(sourceInput)
    await user.click(screen.getByRole('button', { name: /create log/i }))

    expect(await screen.findByText(/source.*required/i)).toBeInTheDocument()
  })

  it('submits valid form data', async () => {
    const user = userEvent.setup()
    const mockOnSuccess = jest.fn()
    const mockCreateLog = jest.spyOn(api, 'createLog').mockResolvedValue({
      id: 1,
      timestamp: '2024-01-15T10:30:00Z',
      message: 'Test message',
      severity: 'INFO',
      source: 'test-source'
    })

    render(<CreateForm onSuccess={mockOnSuccess} />)

    await user.clear(screen.getByLabelText(/message/i))
    await user.type(screen.getByLabelText(/message/i), 'Test message')
    await user.clear(screen.getByLabelText(/source/i))
    await user.type(screen.getByLabelText(/source/i), 'test-source')
    await user.click(screen.getByRole('button', { name: /create log/i }))

    await waitFor(() => {
      expect(mockCreateLog).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'Test message',
          source: 'test-source',
        })
      )
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })

  it('disables submit button during submission', async () => {
    const user = userEvent.setup()
    jest.spyOn(api, 'createLog').mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    render(<CreateForm />)

    await user.clear(screen.getByLabelText(/message/i))
    await user.type(screen.getByLabelText(/message/i), 'Test')
    await user.clear(screen.getByLabelText(/source/i))
    await user.type(screen.getByLabelText(/source/i), 'test-source')

    const submitButton = screen.getByRole('button', { name: /create log/i })
    await user.click(submitButton)

    expect(submitButton).toBeDisabled()
  })

  it('handles API error gracefully', async () => {
    const user = userEvent.setup()
    jest.spyOn(api, 'createLog').mockRejectedValue(new Error('API Error'))

    render(<CreateForm />)

    await user.clear(screen.getByLabelText(/message/i))
    await user.type(screen.getByLabelText(/message/i), 'Test')
    await user.clear(screen.getByLabelText(/source/i))
    await user.type(screen.getByLabelText(/source/i), 'test-source')
    await user.click(screen.getByRole('button', { name: /create log/i }))

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /create log/i })).not.toBeDisabled()
    })
  })

  it('has no accessibility violations', async () => {
    const { container } = render(<CreateForm />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
