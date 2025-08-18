import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/router'
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline'

interface Company {
  ticker: string
  name: string
  sector?: string
}

interface SearchBarProps {
  className?: string
}

export default function SearchBar({ className = '' }: SearchBarProps) {
  const router = useRouter()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Company[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const [loading, setLoading] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [suggestions, setSuggestions] = useState<Company[]>([])
  const inputRef = useRef<HTMLInputElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  // Search companies from API
  const searchCompanies = async (searchQuery: string): Promise<Company[]> => {
    try {
      console.log('🔍 Searching for:', searchQuery)
      const response = await fetch(`/api/search/companies?q=${encodeURIComponent(searchQuery)}`)
      if (!response.ok) throw new Error('Search failed')
      
      const data = await response.json()
      console.log('📊 Search results:', data)
      return data.data || []
    } catch (error) {
      console.error('❌ Error searching companies:', error)
      // Fallback to basic filtering if API fails
      const fallbackCompanies: Company[] = [
        { ticker: 'ATW', name: 'Attijariwafa Bank', sector: 'Banks' },
        { ticker: 'WAA', name: 'Wafa Assurance', sector: 'Insurance' },
        { ticker: 'IAM', name: 'Maroc Telecom', sector: 'Telecommunications' },
        { ticker: 'BCP', name: 'Banque Centrale Populaire', sector: 'Banks' },
        { ticker: 'BMCE', name: 'BMCE Bank', sector: 'Banks' },
        { ticker: 'ONA', name: 'Omnium Nord Africain', sector: 'Conglomerates' },
      ]
      
      const filtered = fallbackCompanies.filter(company =>
        company.ticker.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
      console.log('🔄 Fallback results:', filtered)
      return filtered
    }
  }

  useEffect(() => {
    if (query.trim()) {
      setLoading(true)
      // Search with debounce
      const timer = setTimeout(async () => {
        const searchResults = await searchCompanies(query)
        setResults(searchResults)
        setLoading(false)
        setIsOpen(true)
        setSelectedIndex(-1)
      }, 300)

      return () => clearTimeout(timer)
    } else {
      setResults([])
      setIsOpen(false)
      setSelectedIndex(-1)
      // Load suggestions when empty
      ;(async () => {
        try {
          const r = await fetch('/api/search/companies?suggest=1')
          if (r.ok) {
            const d = await r.json()
            setSuggestions(d.data || [])
          }
        } catch {}
      })()
    }
  }, [query])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        inputRef.current &&
        !inputRef.current.contains(event.target as Node) &&
        resultsRef.current &&
        !resultsRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
        // Collapse search bar when clicking outside (only if no query)
        if (!query.trim()) {
          setIsExpanded(false)
          // Dispatch custom event to notify header
          document.dispatchEvent(new CustomEvent('searchStateChange', { 
            detail: { isExpanded: false } 
          }))
        }
      }
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'k' && (event.metaKey || event.ctrlKey)) {
        event.preventDefault()
        inputRef.current?.focus()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleKeyDown)
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [query])

  useEffect(() => {
    return () => {
      if (isExpanded) {
        document.dispatchEvent(new CustomEvent('searchStateChange', { 
          detail: { isExpanded: false } 
        }))
      }
    }
  }, [isExpanded])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        if (!isOpen) return
        e.preventDefault()
        setSelectedIndex(prev => 
          prev < results.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        if (!isOpen) return
        e.preventDefault()
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1)
        break
      case 'Enter':
        e.preventDefault()
        if (selectedIndex >= 0 && results[selectedIndex]) {
          handleSelect(results[selectedIndex])
        } else if (results.length === 1) {
          handleSelect(results[0])
        } else if (results.length > 1) {
          // If multiple results, select the first one
          handleSelect(results[0])
        } else if (query.trim() && results.length === 0 && !loading) {
          // If there's a query but no results, try to search again
          // This handles the case where the user hits Enter before results load
          searchCompanies(query).then(searchResults => {
            if (searchResults.length > 0) {
              handleSelect(searchResults[0])
            }
          })
        }
        break
      case 'Escape':
        handleEscape()
        break
    }
  }

  const handleSelect = (company: Company) => {
    setQuery('')
    setIsOpen(false)
    setSelectedIndex(-1)
    router.push(`/company/${company.ticker}`)
  }

  const handleClear = () => {
    setQuery('')
    setIsOpen(false)
    setSelectedIndex(-1)
    inputRef.current?.focus()
  }

  const handleFocus = () => {
    setIsExpanded(true)
    if (query.trim()) {
      setIsOpen(true)
    }
    // Dispatch custom event to notify header
    document.dispatchEvent(new CustomEvent('searchStateChange', { 
      detail: { isExpanded: true } 
    }))
  }

  const handleBlur = () => {
    // Only collapse if there's no query and no results are open
    if (!query.trim() && !isOpen) {
      // Delay collapse to allow for result clicks
      setTimeout(() => {
        if (!query.trim()) {
          setIsExpanded(false)
          // Dispatch custom event to notify header
          document.dispatchEvent(new CustomEvent('searchStateChange', { 
            detail: { isExpanded: false } 
          }))
        }
      }, 200)
    }
  }

  const handleEscape = () => {
    setIsOpen(false)
    inputRef.current?.blur()
    // Collapse search bar on escape (only if no query)
    if (!query.trim()) {
      setIsExpanded(false)
      // Dispatch custom event to notify header
      document.dispatchEvent(new CustomEvent('searchStateChange', { 
        detail: { isExpanded: false } 
      }))
    }
  }

  return (
    <div className={`relative search-bar-wrapper ${className}`}>
      <div className={`relative search-bar-container transition-all duration-300 ease-in-out ${
        isExpanded ? 'w-full' : 'w-12'
      }`}>
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 dark:text-gray-500 z-10" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={isExpanded ? "Search companies... (⌘K)" : ""}
          className={`search-bar-input pl-10 pr-10 py-3 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-casablanca-blue focus:border-transparent transition-all duration-300 ease-in-out ${
            !isExpanded ? 'cursor-pointer' : ''
          }`}
          style={{
            width: isExpanded ? '100%' : '48px',
            minWidth: isExpanded ? 'auto' : '48px',
            maxWidth: '100%',
            height: '44px',
            minHeight: '44px'
          }}
        />
        {query && isExpanded && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors z-10"
          >
            <XMarkIcon className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Results dropdown */}
      {isExpanded && (
        <div
          ref={resultsRef}
          className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-[100] max-h-60 overflow-y-auto min-w-0"
        >
          {loading && (
            <div className="p-4 text-center text-gray-500 dark:text-gray-400">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-casablanca-blue mx-auto"></div>
              <p className="mt-2 text-sm">Searching...</p>
            </div>
          )}
          {!loading && query.trim() && results.length > 0 && (
            <div className="py-1">
              {results.map((company, index) => (
                <button
                  key={company.ticker}
                  onClick={() => handleSelect(company)}
                  className={`w-full px-4 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                    index === selectedIndex ? 'bg-gray-50 dark:bg-gray-700' : ''
                  }`}
                >
                  <div className="flex items-center justify-between min-w-0">
                    <div className="min-w-0 flex-1">
                      <div className="font-medium text-gray-900 dark:text-white truncate">
                        {company.ticker}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400 truncate">
                        {company.name}
                      </div>
                    </div>
                    {company.sector && (
                      <div className="text-xs text-gray-400 dark:text-gray-500 bg-gray-100 dark:bg-gray-600 px-2 py-1 rounded flex-shrink-0 ml-2">
                        {company.sector}
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
          {!loading && query.trim() && results.length === 0 && (
            <div className="p-4 text-center text-gray-500 dark:text-gray-400">
              <p className="text-sm">No companies found</p>
              <p className="text-xs mt-1">Try searching by ticker or company name</p>
            </div>
          )}
          {!loading && !query.trim() && (
            <div className="p-4 text-gray-700 dark:text-gray-200">
              <div className="text-xs uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-2">Suggested</div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {suggestions.map((s) => (
                  <button
                    key={s.ticker}
                    onClick={() => handleSelect(s)}
                    className="px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 text-left"
                  >
                    <div className="font-medium text-gray-900 dark:text-white">{s.ticker}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 truncate">{s.name}</div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
} 