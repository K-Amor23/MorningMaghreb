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
  const inputRef = useRef<HTMLInputElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  // Search companies from API
  const searchCompanies = async (searchQuery: string): Promise<Company[]> => {
    try {
      const response = await fetch(`/api/search/companies?q=${encodeURIComponent(searchQuery)}`)
      if (!response.ok) throw new Error('Search failed')
      
      const data = await response.json()
      return data.data || []
    } catch (error) {
      console.error('Error searching companies:', error)
      // Fallback to basic filtering if API fails
      const fallbackCompanies: Company[] = [
        { ticker: 'ATW', name: 'Attijariwafa Bank', sector: 'Banks' },
        { ticker: 'IAM', name: 'Maroc Telecom', sector: 'Telecommunications' },
        { ticker: 'BCP', name: 'Banque Centrale Populaire', sector: 'Banks' },
        { ticker: 'BMCE', name: 'BMCE Bank', sector: 'Banks' },
        { ticker: 'ONA', name: 'Omnium Nord Africain', sector: 'Conglomerates' },
      ]
      
      return fallbackCompanies.filter(company =>
        company.ticker.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
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
      }
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl/Cmd + K to focus search
      if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
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
  }, [])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(prev => 
          prev < results.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1)
        break
      case 'Enter':
        e.preventDefault()
        if (selectedIndex >= 0 && results[selectedIndex]) {
          handleSelect(results[selectedIndex])
        } else if (results.length === 1) {
          handleSelect(results[0])
        }
        break
      case 'Escape':
        setIsOpen(false)
        inputRef.current?.blur()
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

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => query.trim() && setIsOpen(true)}
          placeholder="Search companies... (⌘K)"
          className="w-full pl-10 pr-10 py-2 text-sm border border-gray-300 dark:border-dark-border rounded-lg bg-white dark:bg-dark-card text-gray-900 dark:text-dark-text placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-casablanca-blue focus:border-transparent"
        />
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <XMarkIcon className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Results dropdown */}
      {isOpen && (
        <div
          ref={resultsRef}
          className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto"
        >
          {loading ? (
            <div className="p-4 text-center text-gray-500 dark:text-gray-400">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-casablanca-blue mx-auto"></div>
              <p className="mt-2 text-sm">Searching...</p>
            </div>
          ) : results.length > 0 ? (
            <div className="py-1">
              {results.map((company, index) => (
                <button
                  key={company.ticker}
                  onClick={() => handleSelect(company)}
                  className={`w-full px-4 py-2 text-left hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors ${
                    index === selectedIndex ? 'bg-gray-50 dark:bg-dark-hover' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">
                        {company.ticker}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {company.name}
                      </div>
                    </div>
                    {company.sector && (
                      <div className="text-xs text-gray-400 dark:text-gray-500 bg-gray-100 dark:bg-dark-border px-2 py-1 rounded">
                        {company.sector}
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          ) : query.trim() ? (
            <div className="p-4 text-center text-gray-500 dark:text-gray-400">
              <p className="text-sm">No companies found</p>
              <p className="text-xs mt-1">Try searching by ticker or company name</p>
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
} 