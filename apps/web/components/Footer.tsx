import Link from 'next/link'
import { ChartBarIcon } from '@heroicons/react/24/outline'

export default function Footer() {
  return (
    <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Brand Section */}
          <div className="md:col-span-2">
            <div className="flex items-center space-x-2 mb-2">
              <ChartBarIcon className="h-5 w-5 text-casablanca-blue" />
              <span className="text-lg font-bold text-casablanca-blue">
                Morning Maghreb
              </span>
            </div>
            <p className="text-gray-500 dark:text-gray-400 text-sm mb-3">
              Morocco's premier market research & analytics platform with 79+ companies and real-time data.
            </p>
            <div className="flex flex-wrap gap-4 text-xs text-gray-400 dark:text-gray-500">
              <span>🇲🇦 Moroccan Market Data</span>
              <span>📊 79 Companies</span>
              <span>🤖 AI-Powered Insights</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-400 dark:text-gray-300 uppercase mb-3">
              Platform
            </h3>
            <ul className="space-y-2">
              <li>
                <Link href="/markets" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Markets
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/contest" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Contest
                </Link>
              </li>
              <li>
                <Link href="/paper-trading" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Paper Trading
                </Link>
              </li>
            </ul>
          </div>

          {/* Support Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-400 dark:text-gray-300 uppercase mb-3">
              Support
            </h3>
            <ul className="space-y-2">
              <li>
                <Link href="/help" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Help
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Privacy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Terms
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-col sm:flex-row justify-between items-center">
            <p className="text-sm text-gray-400 dark:text-gray-500">
              &copy; 2024 Morning Maghreb. All rights reserved.
            </p>
            <div className="mt-2 sm:mt-0 flex space-x-4 text-xs text-gray-400 dark:text-gray-500">
              <Link href="/about" className="hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                About
              </Link>
              <Link href="/newsletter" className="hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                Newsletter
              </Link>
              <Link href="/api/docs" className="hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                API
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
} 