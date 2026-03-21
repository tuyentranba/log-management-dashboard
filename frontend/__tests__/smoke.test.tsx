import { render, screen } from './utils/test-utils'

describe('Test Infrastructure', () => {
  it('renders a component', () => {
    render(<div>Hello Test</div>)
    expect(screen.getByText('Hello Test')).toBeInTheDocument()
  })

  it('can use Jest matchers', () => {
    expect(1 + 1).toBe(2)
  })
})
