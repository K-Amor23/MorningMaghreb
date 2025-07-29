import React, { useState, useRef, useCallback, useEffect } from 'react'
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { useRouter } from 'next/router'
import useSWR from 'swr'
import { fetcher } from '@/lib/api'
import { ARIA_LABELS } from '@/lib/accessibility'
import { useLocalStorage } from '@/lib/useClientOnly'

interface SearchResult {
  ticker: string
  name: string
  sector?: string
  market_cap?: number
  price?: number
  change?: number
}

interface EnhancedSearchProps {
  placeholder?: string
  className?: string
  onSearch?: (query: string) => void
  showSuggestions?: boolean
  maxSuggestions?: number
}

// Fuzzy search implementation
const fuzzySearch = (query: string, items: SearchResult[]): SearchResult[] => {
  const searchTerm = query.toLowerCase()
  return items
    .filter(item =>
      item.ticker.toLowerCase().includes(searchTerm) ||
      item.name.toLowerCase().includes(searchTerm) ||
      item.sector?.toLowerCase().includes(searchTerm)
    )
    .sort((a, b) => {
      // Prioritize exact ticker matches
      if (a.ticker.toLowerCase() === searchTerm) return -1
      if (b.ticker.toLowerCase() === searchTerm) return 1

      // Then prioritize ticker starts with
      if (a.ticker.toLowerCase().startsWith(searchTerm)) return -1
      if (b.ticker.toLowerCase().startsWith(searchTerm)) return 1

      // Then by name starts with
      if (a.name.toLowerCase().startsWith(searchTerm)) return -1
      if (b.name.toLowerCase().startsWith(searchTerm)) return 1

      return 0
    })
}

export default function EnhancedSearch({
  placeholder = 'Search stocks, companies, or news...',
  className = '',
  onSearch,
  showSuggestions = true,
  maxSuggestions = 8
}: EnhancedSearchProps) {
  const router = useRouter()
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const [recentSearches, setRecentSearches] = useLocalStorage<string[]>('recent-searches', [])
  const inputRef = useRef<HTMLInputElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Fetch search suggestions
  const { data: suggestions, error } = useSWR<SearchResult[]>(
    query.length >= 2 ? '/api/search/suggestions?q=' + encodeURIComponent(query) : null,
    fetcher
  )

  const filteredResults = useCallback(() => {
    if (!suggestions) return []

    const fuzzyResults = fuzzySearch(query, suggestions)
    return fuzzyResults.slice(0, maxSuggestions)
  }, [suggestions, query, maxSuggestions])

  // Save recent searches to localStorage
  const saveRecentSearch = useCallback((searchTerm: string) => {
    const updated = [searchTerm, ...recentSearches.filter(s => s !== searchTerm)].slice(0, 5)
    setRecentSearches(updated)
  }, [recentSearches, setRecentSearches])

  // Handle search submission
  const handleSearch = useCallback((searchQuery: string) => {
    if (!searchQuery.trim()) return

    saveRecentSearch(searchQuery)
    setIsOpen(false)
    setSelectedIndex(-1)

    if (onSearch) {
      onSearch(searchQuery)
    } else {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`)
    }
  }, [onSearch, router, saveRecentSearch])

  // Handle keyboard navigation
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    const results = filteredResults()
    const totalItems = results.length + (recentSearches.length > 0 ? 1 : 0)

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(prev => Math.min(prev + 1, totalItems - 1))
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(prev => Math.max(prev - 1, -1))
        break
      case 'Enter':
        e.preventDefault()
        if (selectedIndex >= 0) {
          if (selectedIndex < results.length) {
            handleSearch(results[selectedIndex].ticker)
          } else {
            const recentIndex = selectedIndex - results.length
            handleSearch(recentSearches[recentIndex])
          }
        } else {
          handleSearch(query)
        }
        break
      case 'Escape':
        setIsOpen(false)
        setSelectedIndex(-1)
        inputRef.current?.blur()
        break
    }
  }, [filteredResults, recentSearches, selectedIndex, query, handleSearch])

  // Handle input changes
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)
    setIsOpen(value.length >= 2)
    setSelectedIndex(-1)
  }, [])

  // Handle input focus
  const handleInputFocus = useCallback(() => {
    if (query.length >= 2 || recentSearches.length > 0) {
      setIsOpen(true)
    }
  }, [query, recentSearches])

  // Handle input blur
  const handleInputBlur = useCallback(() => {
    // Delay to allow for clicks on suggestions
    setTimeout(() => setIsOpen(false), 200)
  }, [])

  // Clear search
  const handleClear = useCallback(() => {
    setQuery('')
    setIsOpen(false)
    setSelectedIndex(-1)
    inputRef.current?.focus()
  }, [])

  const results = filteredResults()

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          aria-label={ARIA_LABELS.SEARCH_INPUT}
          className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-casablanca-blue focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400"
        />
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            aria-label="Clear search"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Search suggestions dropdown */}
      {isOpen && showSuggestions && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-96 overflow-y-auto"
        >
          {/* Search results */}
          {results.length > 0 && (
            <div>
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                Search Results
              </div>
              {results.map((result, index) => (
                <button
                  key={result.ticker}
                  onClick={() => handleSearch(result.ticker)}
                  className={`w-full px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 ${selectedIndex === index ? 'bg-gray-50 dark:bg-gray-700' : ''
                    }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">
                        {result.ticker}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {result.name}
                      </div>
                    </div>
                    {result.price && (
                      <div className="text-right">
                        <div className="font-medium text-gray-900 dark:text-white">
                          {result.price.toFixed(2)}
                        </div>
                        {result.change && (
                          <div className={`text-sm ${result.change >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                            {result.change >= 0 ? '+' : ''}{result.change.toFixed(2)}%
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Recent searches */}
          {recentSearches.length > 0 && (
            <div>
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                Recent Searches
              </div>
              {recentSearches.map((search, index) => (
                <button
                  key={search}
                  onClick={() => handleSearch(search)}
                  className={`w-full px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 ${selectedIndex === results.length + index ? 'bg-gray-50 dark:bg-gray-700' : ''
                    }`}
                >
                  <div className="flex items-center">
                    <MagnifyingGlassIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-gray-900 dark:text-white">{search}</span>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* No results */}
          {results.length === 0 && recentSearches.length === 0 && query.length >= 2 && (
            <div className="px-3 py-4 text-center text-gray-500 dark:text-gray-400">
              No results found for "{query}"
            </div>
          )}
        </div>
      )}
    </div>
  )
} 