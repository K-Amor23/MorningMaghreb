import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { useUser } from '../lib'
import {
  UserCircleIcon,
  Cog6ToothIcon,
  CreditCardIcon,
  ArrowRightOnRectangleIcon,
  UserIcon,
  EnvelopeIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  BellIcon,
  HeartIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline'
import {
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/solid'

export default function AccountDropdown() {
  const { user, profile, loading, signOut } = useUser()
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false)
      }
    }
    if (showDropdown) {
      document.addEventListener('mousedown', handleClickOutside)
    } else {
      document.removeEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showDropdown])

  const handleSignOut = async () => {
    await signOut()
    setShowDropdown(false)
  }

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'pro':
        return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20'
      case 'admin':
        return 'text-purple-600 bg-purple-50 dark:bg-purple-900/20'
      default:
        return 'text-gray-600 bg-gray-50 dark:bg-gray-700'
    }
  }

  const getTierLabel = (tier: string) => {
    switch (tier) {
      case 'pro':
        return 'Premium'
      case 'admin':
        return 'Admin'
      default:
        return 'Free'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center space-x-4">
        <div className="animate-pulse bg-gray-200 dark:bg-gray-700 rounded-full h-8 w-8"></div>
      </div>
    )
  }

  return (
    <div className="relative z-[150]" ref={dropdownRef}>
      {/* Account Button */}
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center space-x-2 p-2 text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-gray-100 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
        aria-label="Account menu"
      >
        {user ? (
          <>
            <div className="relative">
              <UserCircleIcon className="h-6 w-6" />
              {profile?.tier === 'pro' && (
                <div className="absolute -top-1 -right-1 h-3 w-3 bg-yellow-500 rounded-full border-2 border-white dark:border-gray-800"></div>
              )}
            </div>
            <div className="hidden sm:block text-left">
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {profile?.full_name || user.email?.split('@')[0] || 'User'}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {getTierLabel(profile?.tier || 'free')}
              </div>
            </div>
          </>
        ) : (
          <UserCircleIcon className="h-6 w-6" />
        )}
      </button>

      {/* Dropdown Menu */}
      {showDropdown && (
        <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-[150]">
          {user ? (
            // Logged in user menu
            <div className="py-2">
              {/* User Info Header */}
              <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <UserCircleIcon className="h-10 w-10 text-gray-400" />
                    {profile?.tier === 'pro' && (
                      <div className="absolute -top-1 -right-1 h-4 w-4 bg-yellow-500 rounded-full border-2 border-white dark:border-gray-800"></div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {profile?.full_name || user.email?.split('@')[0] || 'User'}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                      {user.email}
                    </div>
                    <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium mt-1 ${getTierColor(profile?.tier || 'free')}`}>
                      {profile?.tier === 'pro' && <ShieldCheckIcon className="h-3 w-3 mr-1" />}
                      {getTierLabel(profile?.tier || 'free')}
                    </div>
                  </div>
                </div>
              </div>

              {/* Menu Items */}
              <div className="py-1">
                <Link
                  href="/account/settings"
                  className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  onClick={() => setShowDropdown(false)}
                >
                  <Cog6ToothIcon className="h-4 w-4 mr-3" />
                  Account Settings
                </Link>

                <Link
                  href="/dashboard"
                  className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  onClick={() => setShowDropdown(false)}
                >
                  <ChartBarIcon className="h-4 w-4 mr-3" />
                  Dashboard
                </Link>

                <Link
                  href="/portfolio"
                  className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  onClick={() => setShowDropdown(false)}
                >
                  <HeartIcon className="h-4 w-4 mr-3" />
                  Watchlist
                </Link>

                <Link
                  href="/account/alerts"
                  className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  onClick={() => setShowDropdown(false)}
                >
                  <BellIcon className="h-4 w-4 mr-3" />
                  Alerts & Notifications
                </Link>

                <Link
                  href="/paper-trading"
                  className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  onClick={() => setShowDropdown(false)}
                >
                  <CurrencyDollarIcon className="h-4 w-4 mr-3" />
                  Paper Trading
                </Link>

                {profile?.tier === 'free' && (
                  <Link
                    href="/premium"
                    className="flex items-center px-4 py-2 text-sm text-yellow-600 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 transition-colors"
                    onClick={() => setShowDropdown(false)}
                  >
                    <CreditCardIcon className="h-4 w-4 mr-3" />
                    Upgrade to Premium
                  </Link>
                )}

                {profile?.tier === 'pro' && (
                  <Link
                    href="/premium"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    onClick={() => setShowDropdown(false)}
                  >
                    <CreditCardIcon className="h-4 w-4 mr-3" />
                    Manage Subscription
                  </Link>
                )}

                <div className="border-t border-gray-200 dark:border-gray-700 my-1"></div>

                <button
                  onClick={handleSignOut}
                  className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <ArrowRightOnRectangleIcon className="h-4 w-4 mr-3" />
                  Sign Out
                </button>
              </div>
            </div>
          ) : (
            // Guest user menu
            <div className="py-2">
              <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                <div className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                  Welcome to Casablanca Insight
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Sign in to access your personalized dashboard
                </div>
              </div>

              <div className="py-1">
                <Link
                  href="/login"
                  className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  onClick={() => setShowDropdown(false)}
                >
                  <UserIcon className="h-4 w-4 mr-3" />
                  Sign In
                </Link>

                <Link
                  href="/signup"
                  className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  onClick={() => setShowDropdown(false)}
                >
                  <EnvelopeIcon className="h-4 w-4 mr-3" />
                  Create Account
                </Link>

                <div className="border-t border-gray-200 dark:border-gray-700 my-1"></div>

                <Link
                  href="/premium"
                  className="flex items-center px-4 py-2 text-sm text-yellow-600 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 transition-colors"
                  onClick={() => setShowDropdown(false)}
                >
                  <ShieldCheckIcon className="h-4 w-4 mr-3" />
                  Explore Premium Features
                </Link>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
} 