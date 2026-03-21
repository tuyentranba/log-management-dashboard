'use client'

import { useState, useEffect } from 'react'
import { useQueryState } from 'nuqs'
import { useDebounce } from '@/hooks/use-debounce'
import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'

export function SearchInput() {
  const [search, setSearch] = useQueryState('search', { defaultValue: '' })
  const [localValue, setLocalValue] = useState(search)
  const debouncedSearch = useDebounce(localValue, 400) // 400ms delay per 03-CONTEXT.md line 43

  // Update URL only after debounce
  useEffect(() => {
    setSearch(debouncedSearch || null)
  }, [debouncedSearch, setSearch])

  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
      <Input
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder="Search messages..."
        className="pl-10"
      />
    </div>
  )
}
