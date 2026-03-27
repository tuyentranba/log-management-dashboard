import { toDatetimeLocalString } from '@/lib/date-utils'

describe('date-utils', () => {
  describe('toDatetimeLocalString', () => {
    it('converts Date to datetime-local format', () => {
      const date = new Date('2024-01-15T10:30:00Z')
      const result = toDatetimeLocalString(date)

      // Format should be YYYY-MM-DDTHH:mm:ss (local time)
      expect(result).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/)
    })

    it('defaults to current time when no argument provided', () => {
      const result = toDatetimeLocalString()

      // Should return a valid datetime-local string with seconds
      expect(result).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/)
    })

    it('handles timezone conversion correctly', () => {
      // Create a date at midnight UTC
      const utcDate = new Date('2024-01-15T00:00:00Z')
      const result = toDatetimeLocalString(utcDate)

      // Result should be in local timezone (format validation)
      expect(result).toMatch(/^2024-01-\d{2}T\d{2}:\d{2}:\d{2}$/)
    })
  })
})
