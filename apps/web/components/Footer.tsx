import Link from 'next/link'
import { ChartBarIcon, TrophyIcon, CurrencyDollarIcon, NewspaperIcon, CogIcon, UserGroupIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'

export default function Footer() {
  return (
    <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="xl:grid xl:grid-cols-4 xl:gap-8">
          {/* Brand Section */}
          <div className="space-y-6 xl:col-span-1">
            <div className="flex items-center space-x-2">
              <ChartBarIcon className="h-6 w-6 text-casablanca-blue" />
              <span className="text-lg font-bold text-casablanca-blue">
                Casablanca Insights
              </span>
            </div>
            <p className="text-gray-500 dark:text-gray-400 text-sm">
              Morocco's premier market research & analytics platform with 79+ companies, real-time data, and AI-powered insights.
            </p>
            <div className="flex space-x-4">
              <div className="text-xs text-gray-400 dark:text-gray-500">
                <div className="font-semibold">Real Data Coverage</div>
                <div>79 Moroccan Companies</div>
                <div>Live Market Data</div>
              </div>
            </div>
          </div>

          {/* Platform Features */}
          <div className="mt-8 xl:mt-0">
            <h3 className="text-sm font-semibold text-gray-400 dark:text-gray-300 tracking-wider uppercase flex items-center">
              <CogIcon className="h-4 w-4 mr-2" />
              Platform
            </h3>
            <ul className="mt-4 space-y-3">
              <li>
                <Link href="/markets" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Markets Overview
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/portfolio" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Portfolio Tracker
                </Link>
              </li>
              <li>
                <Link href="/watchlists" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Watchlists
                </Link>
              </li>
              <li>
                <Link href="/alerts" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Price Alerts
                </Link>
              </li>
              <li>
                <Link href="/macro" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Macro Analysis
                </Link>
              </li>
            </ul>
          </div>

          {/* Trading & Premium */}
          <div className="mt-8 xl:mt-0">
            <h3 className="text-sm font-semibold text-gray-400 dark:text-gray-300 tracking-wider uppercase flex items-center">
              <CurrencyDollarIcon className="h-4 w-4 mr-2" />
              Trading & Premium
            </h3>
            <ul className="mt-4 space-y-3">
              <li>
                <Link href="/paper-trading" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Paper Trading
                </Link>
              </li>
              <li>
                <Link href="/paper-trading/thinkorswim" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  ThinkOrSwim Interface
                </Link>
              </li>
              <li>
                <Link href="/premium" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Premium Features
                </Link>
              </li>
              <li>
                <Link href="/premium-features" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Advanced Analytics
                </Link>
              </li>
              <li>
                <Link href="/advanced-features" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  AI Insights
                </Link>
              </li>
              <li>
                <Link href="/convert" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Currency Converter
                </Link>
              </li>
            </ul>
          </div>

          {/* Community & News */}
          <div className="mt-8 xl:mt-0">
            <h3 className="text-sm font-semibold text-gray-400 dark:text-gray-300 tracking-wider uppercase flex items-center">
              <UserGroupIcon className="h-4 w-4 mr-2" />
              Community & News
            </h3>
            <ul className="mt-4 space-y-3">
              <li>
                <Link href="/contest" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors flex items-center">
                  <TrophyIcon className="h-3 w-3 mr-1" />
                  Trading Contest
                </Link>
              </li>
              <li>
                <Link href="/news" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors flex items-center">
                  <NewspaperIcon className="h-3 w-3 mr-1" />
                  Market News
                </Link>
              </li>
              <li>
                <Link href="/newsletter" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                  Morning Maghreb
                </Link>
              </li>
              <li>
                <Link href="/compliance" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors flex items-center">
                  <ShieldCheckIcon className="h-3 w-3 mr-1" />
                  Market Guide
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-12 border-t border-gray-200 dark:border-gray-700 pt-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Company Links */}
            <div>
              <h4 className="text-sm font-semibold text-gray-400 dark:text-gray-300 tracking-wider uppercase mb-4">
                Company
              </h4>
              <ul className="space-y-2">
                <li>
                  <Link href="/about" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link href="/contact" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                    Contact
                  </Link>
                </li>
                <li>
                  <Link href="/privacy" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link href="/terms" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                    Terms of Service
                  </Link>
                </li>
              </ul>
            </div>

            {/* Data & API */}
            <div>
              <h4 className="text-sm font-semibold text-gray-400 dark:text-gray-300 tracking-wider uppercase mb-4">
                Data & API
              </h4>
              <ul className="space-y-2">
                <li>
                  <Link href="/api/docs" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                    API Documentation
                  </Link>
                </li>
                <li>
                  <Link href="/data-sources" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                    Data Sources
                  </Link>
                </li>
                <li>
                  <Link href="/market-data" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                    Market Data
                  </Link>
                </li>
                <li>
                  <Link href="/data-quality" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                    Data Quality
                  </Link>
                </li>
              </ul>
            </div>

            {/* Support */}
            <div>
              <h4 className="text-sm font-semibold text-gray-400 dark:text-gray-300 tracking-wider uppercase mb-4">
                Support
              </h4>
              <ul className="space-y-2">
                <li>
                  <Link href="/help" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link href="/faq" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                    FAQ
                  </Link>
                </li>
                <li>
                  <Link href="/feedback" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                    Feedback
                  </Link>
                </li>
                <li>
                  <Link href="/status" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
                    System Status
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          {/* Copyright */}
          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-sm text-gray-400 dark:text-gray-500">
                &copy; 2024 Casablanca Insights. All rights reserved.
              </p>
              <div className="mt-4 md:mt-0 flex space-x-6">
                <span className="text-xs text-gray-400 dark:text-gray-500">
                  🇲🇦 Powered by Moroccan Market Data
                </span>
                <span className="text-xs text-gray-400 dark:text-gray-500">
                  📊 79 Companies • Real-time Data
                </span>
                <span className="text-xs text-gray-400 dark:text-gray-500">
                  🤖 AI-Powered Insights
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
} 