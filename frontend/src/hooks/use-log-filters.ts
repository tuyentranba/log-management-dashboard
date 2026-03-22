import { useQueryStates, parseAsString, parseAsArrayOf } from 'nuqs'

/**
 * Shared filter schema for log filtering across components.
 *
 * This hook provides a single source of truth for log filter state
 * management via URL query parameters. All components that need to
 * read or write filter state should use this hook to ensure consistency.
 *
 * @see docs/decisions/001-filter-reactivity-refactor.md
 */
const logFiltersSchema = {
  search: parseAsString,
  severity: parseAsArrayOf(parseAsString),
  source: parseAsString,
  date_from: parseAsString,
  date_to: parseAsString,
  sort: parseAsString.withDefault('timestamp'),
  order: parseAsString.withDefault('desc'),
}

/**
 * Custom hook for managing log filter state via URL query parameters.
 *
 * Returns the same interface as nuqs useQueryStates:
 * - filters: Current filter state from URL
 * - setFilters: Function to update filters in URL
 *
 * @example
 * ```tsx
 * const [filters, setFilters] = useLogFilters()
 *
 * // Read filters
 * console.log(filters.severity) // ['ERROR', 'CRITICAL']
 *
 * // Update filters
 * setFilters({ severity: ['INFO'] })
 * ```
 */
export function useLogFilters() {
  return useQueryStates(logFiltersSchema)
}

/**
 * TypeScript type for the filter state returned by useLogFilters.
 * Use this type when you need to type filter parameters in functions.
 *
 * @example
 * ```tsx
 * function processFilters(filters: LogFiltersState) {
 *   // filters is properly typed
 * }
 * ```
 */
export type LogFiltersState = ReturnType<typeof useLogFilters>[0]

/**
 * TypeScript type for the setter function returned by useLogFilters.
 *
 * @example
 * ```tsx
 * function MyComponent({ setFilters }: { setFilters: LogFiltersSetter }) {
 *   setFilters({ search: 'error' })
 * }
 * ```
 */
export type LogFiltersSetter = ReturnType<typeof useLogFilters>[1]
