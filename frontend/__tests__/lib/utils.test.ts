import { cn } from '@/lib/utils'

describe('utils', () => {
  describe('cn', () => {
    it('combines class names', () => {
      expect(cn('class1', 'class2')).toBe('class1 class2')
    })

    it('handles conditional classes', () => {
      expect(cn('base', false && 'conditional', 'always')).toBe('base always')
    })

    it('merges Tailwind classes correctly', () => {
      // tailwind-merge deduplicates conflicting classes
      expect(cn('px-2', 'px-4')).toBe('px-4')
    })
  })
})
