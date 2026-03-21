import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'

// Add providers here as needed (e.g., theme, query client)
function AllTheProviders({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}

// Custom render function that wraps with providers
function customRender(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { wrapper: AllTheProviders, ...options })
}

// Re-export everything from React Testing Library
export * from '@testing-library/react'
export { customRender as render }
