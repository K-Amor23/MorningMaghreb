import Link from 'next/link'
import { useTranslation } from 'react-i18next'
import { useState, useRef, useEffect } from 'react'
import { 
  ChartBarIcon, 
  GlobeAltIcon,
  BellIcon,
  UserCircleIcon,
  MagnifyingGlassIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import ThemeToggle from './ThemeToggle'
import SearchBar from './SearchBar'

export default function Header() {
  const { t, i18n } = useTranslation()
  const [showMobileSearch, setShowMobileSearch] = useState(false)
  const [showLangDropdown, setShowLangDropdown] = useState(false)
  const langDropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        langDropdownRef.current &&
        !langDropdownRef.current.contains(event.target as Node)
      ) {
        setShowLangDropdown(false)
      }
    }
    if (showLangDropdown) {
      document.addEventListener('mousedown', handleClickOutside)
    } else {
      document.removeEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showLangDropdown])

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
    <header className="bg-white dark:bg-dark-card shadow-sm border-b border-gray-200 dark:border-dark-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <ChartBarIcon className="h-8 w-8 text-casablanca-blue" />
              <span className="text-xl font-bold text-casablanca-blue">
                Casablanca Insight
              </span>
            </Link>
          </div>

          {/* Search Bar */}
          <div className="hidden md:block flex-1 max-w-md mx-8">
            <SearchBar />
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              href="/dashboard" 
              className="text-gray-700 dark:text-dark-text hover:text-casablanca-blue dark:hover:text-casablanca-blue px-3 py-2 text-sm font-medium transition-colors"
            >
              Dashboard
            </Link>
            <Link 
              href="/markets" 
              className="text-gray-700 dark:text-dark-text hover:text-casablanca-blue dark:hover:text-casablanca-blue px-3 py-2 text-sm font-medium transition-colors"
            >
              Markets
            </Link>
            <Link 
              href="/portfolio" 
              className="text-gray-700 dark:text-dark-text hover:text-casablanca-blue dark:hover:text-casablanca-blue px-3 py-2 text-sm font-medium transition-colors"
            >
              Portfolio
            </Link>
            <Link 
              href="/news" 
              className="text-gray-700 dark:text-dark-text hover:text-casablanca-blue dark:hover:text-casablanca-blue px-3 py-2 text-sm font-medium transition-colors"
            >
              News
            </Link>
            <Link 
              href="/advanced-features" 
              className="text-gray-700 dark:text-dark-text hover:text-casablanca-blue dark:hover:text-casablanca-blue px-3 py-2 text-sm font-medium transition-colors"
            >
              Advanced
            </Link>
            <Link 
              href="/premium" 
              className="text-sm text-yellow-600 font-semibold hover:underline px-3 py-2 transition-colors"
            >
              Premium
            </Link>
          </nav>

          {/* Right side actions */}
          <div className="flex items-center space-x-4">
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
                <div className="absolute right-0 mt-2 w-36 bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg shadow-lg z-50">
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
            
            {/* User menu */}
            <button className="p-2 text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-gray-100 transition-colors">
              <UserCircleIcon className="h-6 w-6" />
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Search Modal */}
      {showMobileSearch && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 md:hidden">
          <div className="bg-white dark:bg-dark-card p-4">
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