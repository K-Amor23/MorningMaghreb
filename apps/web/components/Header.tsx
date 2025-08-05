import Link from 'next/link'
import { useTranslation } from 'react-i18next'
import { useState, useRef, useEffect } from 'react'
import {
  ChartBarIcon,
  GlobeAltIcon,
  BellIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
  Cog6ToothIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline'
import ThemeToggle from './ThemeToggle'
import SearchBar from './SearchBar'
import AccountDropdown from './AccountDropdown'
import { useAuth } from '../hooks/useAuth'

export default function Header() {
  const { i18n } = useTranslation()
  const { user } = useAuth()
  const [showMobileSearch, setShowMobileSearch] = useState(false)
  const [showLangDropdown, setShowLangDropdown] = useState(false)
  const [showMarketsDropdown, setShowMarketsDropdown] = useState(false)
  const [isSearchExpanded, setIsSearchExpanded] = useState(false)
  const langDropdownRef = useRef<HTMLDivElement>(null)
  const marketsDropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        langDropdownRef.current &&
        !langDropdownRef.current.contains(event.target as Node)
      ) {
        setShowLangDropdown(false)
      }
      if (
        marketsDropdownRef.current &&
        !marketsDropdownRef.current.contains(event.target as Node)
      ) {
        setShowMarketsDropdown(false)
      }
    }
    if (showLangDropdown || showMarketsDropdown) {
      document.addEventListener('mousedown', handleClickOutside)
    } else {
      document.removeEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showLangDropdown, showMarketsDropdown])

  // Listen for search expansion state changes
  useEffect(() => {
    const handleSearchStateChange = (event: CustomEvent) => {
      setIsSearchExpanded(event.detail.isExpanded)
    }

    document.addEventListener('searchStateChange', handleSearchStateChange as EventListener)
    return () => {
      document.removeEventListener('searchStateChange', handleSearchStateChange as EventListener)
    }
  }, [])

  const languages = [
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'fr', label: 'Français', flag: '🇫🇷' },
    { code: 'ar', label: 'العربية', flag: '🇲🇦' },
  ]

  const handleLanguageChange = (code: string) => {
    i18n.changeLanguage(code)
    setShowLangDropdown(false)
  }

  return (
    <header className="bg-white dark:bg-dark-card shadow-sm border-b border-gray-200 dark:border-dark-border relative z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20 py-2 gap-4">
          {/* Logo and Brand */}
          <div className={`flex items-center flex-shrink-0 transition-all duration-300 ${isSearchExpanded ? 'opacity-0 scale-95' : 'opacity-100 scale-100'
            }`}>
            <Link href="/" className="flex items-center space-x-2">
              <ChartBarIcon className="h-8 w-8 text-casablanca-blue" />
              <span className="text-xl font-bold text-casablanca-blue">
                Morning Maghreb
              </span>
            </Link>
          </div>

          {/* Search Bar - Takes full width when expanded */}
          <div className={`hidden md:block transition-all duration-300 flex items-center justify-center flex-1 ${isSearchExpanded
            ? 'max-w-2xl mx-4'
            : 'max-w-lg mx-8'
            }`}>
            <SearchBar />
          </div>

          {/* Navigation - Hidden when search is expanded */}
          <nav className={`hidden md:flex items-center space-x-4 flex-shrink-0 transition-all duration-300 ${isSearchExpanded
            ? 'opacity-0 scale-95 pointer-events-none'
            : 'opacity-100 scale-100'
            }`}>
            {/* Markets Dropdown */}
            <div className="relative" ref={marketsDropdownRef}>
              <button
                onClick={() => setShowMarketsDropdown(!showMarketsDropdown)}
                className="flex items-center space-x-1 text-gray-700 dark:text-dark-text hover:text-casablanca-blue dark:hover:text-casablanca-blue px-2 py-2 text-sm font-medium transition-colors"
              >
                <span>Markets</span>
                <ChevronDownIcon className="h-4 w-4" />
              </button>

              {showMarketsDropdown && (
                <div className="absolute left-0 mt-2 w-64 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg shadow-lg z-[100]">
                  <div className="py-2">
                    <div className="px-4 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Asset Classes
                    </div>
                    <Link
                      href="/markets"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors"
                      onClick={() => setShowMarketsDropdown(false)}
                    >
                      📈 Stocks
                    </Link>
                    <Link
                      href="/markets/bonds"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors"
                      onClick={() => setShowMarketsDropdown(false)}
                    >
                      💰 Bonds
                    </Link>
                    <Link
                      href="/markets/etfs"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors"
                      onClick={() => setShowMarketsDropdown(false)}
                    >
                      📊 ETFs
                    </Link>

                    <div className="border-t border-gray-200 dark:border-gray-700 my-2"></div>

                    <div className="px-4 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Macro Data
                    </div>
                    <Link
                      href="/macro/gdp"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors"
                      onClick={() => setShowMarketsDropdown(false)}
                    >
                      📊 GDP
                    </Link>
                    <Link
                      href="/macro/interest-rates"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors"
                      onClick={() => setShowMarketsDropdown(false)}
                    >
                      💰 Interest Rates
                    </Link>
                    <Link
                      href="/macro/inflation"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors"
                      onClick={() => setShowMarketsDropdown(false)}
                    >
                      📈 Inflation
                    </Link>
                    <Link
                      href="/macro/exchange-rates"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors"
                      onClick={() => setShowMarketsDropdown(false)}
                    >
                      💱 Exchange Rates
                    </Link>
                    <Link
                      href="/macro/trade-balance"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors"
                      onClick={() => setShowMarketsDropdown(false)}
                    >
                      📊 Trade Balance
                    </Link>
                  </div>
                </div>
              )}
            </div>
            <Link
              href="/portfolio"
              className="text-gray-700 dark:text-dark-text hover:text-casablanca-blue dark:hover:text-casablanca-blue px-2 py-2 text-sm font-medium transition-colors"
            >
              Portfolio
            </Link>
            <Link
              href="/news"
              className="text-gray-700 dark:text-dark-text hover:text-casablanca-blue dark:hover:text-casablanca-blue px-2 py-2 text-sm font-medium transition-colors"
            >
              News
            </Link>
            <Link
              href="/newsletter"
              className="text-gray-700 dark:text-dark-text hover:text-casablanca-blue dark:hover:text-casablanca-blue px-2 py-2 text-sm font-medium transition-colors"
            >
              Newsletter
            </Link>
            <Link
              href="/compliance"
              className="text-gray-700 dark:text-dark-text hover:text-casablanca-blue dark:hover:text-casablanca-blue px-2 py-2 text-sm font-medium transition-colors"
            >
              Market Guide
            </Link>
            <Link
              href="/advanced-features"
              className="text-gray-700 dark:text-dark-text hover:text-casablanca-blue dark:hover:text-casablanca-blue px-2 py-2 text-sm font-medium transition-colors"
            >
              Advanced
            </Link>
            <Link
              href="/premium"
              className="text-sm text-yellow-600 font-semibold hover:text-yellow-700 px-2 py-2 transition-colors border border-yellow-600 rounded-lg hover:bg-yellow-50 dark:hover:bg-yellow-900/20"
            >
              Premium
            </Link>
            {user?.role === 'admin' && (
              <Link
                href="/admin"
                className="text-sm text-red-600 font-semibold hover:text-red-700 px-2 py-2 transition-colors border border-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center"
              >
                <Cog6ToothIcon className="h-4 w-4 mr-1" />
                Admin
              </Link>
            )}
          </nav>

          {/* Right side actions - Partially hidden when search is expanded */}
          <div className={`flex items-center space-x-2 flex-shrink-0 transition-all duration-300 ${isSearchExpanded
            ? 'opacity-50 scale-95'
            : 'opacity-100 scale-100'
            }`}>
            {/* Mobile search button */}
            <button
              onClick={() => setShowMobileSearch(true)}
              className="md:hidden p-2 text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-gray-100 transition-colors"
            >
              <MagnifyingGlassIcon className="h-5 w-5" />
            </button>

            {/* Theme toggle */}
            <ThemeToggle />

            {/* Language selector */}
            <div className="relative" ref={langDropdownRef}>
              <button
                className="p-2 text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-gray-100 transition-colors"
                onClick={() => setShowLangDropdown((v) => !v)}
                aria-label="Select language"
              >
                <GlobeAltIcon className="h-5 w-5" />
              </button>
              {showLangDropdown && (
                <div className="absolute right-0 mt-2 w-36 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg shadow-lg z-[100]">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => handleLanguageChange(lang.code)}
                      className={`w-full flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-dark-hover transition-colors ${i18n.language === lang.code ? 'font-bold' : ''}`}
                    >
                      <span className="mr-2 text-lg">{lang.flag}</span> {lang.label}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Notifications */}
            <button className="p-2 text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-gray-100 transition-colors relative">
              <BellIcon className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 bg-morocco-red rounded-full"></span>
            </button>

            {/* Account Dropdown */}
            <AccountDropdown />
          </div>
        </div>
      </div>

      {/* Mobile Search Modal */}
      {showMobileSearch && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-[200] md:hidden">
          <div className="bg-white dark:bg-dark-card p-4 pt-16">
            <div className="flex items-center space-x-2 mb-4">
              <SearchBar className="flex-1" />
              <button
                onClick={() => setShowMobileSearch(false)}
                className="p-2 text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-gray-100"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  )
} 