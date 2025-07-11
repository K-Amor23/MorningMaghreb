import { useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useUser } from '@/lib/useUser'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import CompanyComparison from '@/components/advanced/CompanyComparison'
import EarningsCalendar from '@/components/advanced/EarningsCalendar'
import DividendTracker from '@/components/advanced/DividendTracker'
import EconomicIndicatorTracker from '@/components/advanced/EconomicIndicatorTracker'
import CustomScreens from '@/components/advanced/CustomScreens'
import { 
  ChartBarIcon, 
  CalendarIcon, 
  CurrencyDollarIcon, 
  ChartPieIcon, 
  MagnifyingGlassIcon 
} from '@heroicons/react/24/outline'

type ActiveTab = 'comparison' | 'earnings' | 'dividends' | 'economic' | 'screens'

export default function AdvancedFeatures() {
  const { user, profile, loading } = useUser()
  const [activeTab, setActiveTab] = useState<ActiveTab>('comparison')

  // Check access control
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-casablanca-blue"></div>
      </div>
    )
  }

  const tabs = [
    {
      id: 'comparison' as ActiveTab,
      name: 'Company Comparison',
      icon: ChartBarIcon,
      description: 'Compare 2-3 Moroccan companies side-by-side'
    },
    {
      id: 'earnings' as ActiveTab,
      name: 'Earnings Calendar',
      icon: CalendarIcon,
      description: 'Track upcoming earnings releases and set alerts'
    },
    {
      id: 'dividends' as ActiveTab,
      name: 'Dividend Tracker',
      icon: CurrencyDollarIcon,
      description: 'Monitor dividend events and yields'
    },
    {
      id: 'economic' as ActiveTab,
      name: 'Economic Indicators',
      icon: ChartPieIcon,
      description: 'Track macro trends with AI insights'
    },
    {
      id: 'screens' as ActiveTab,
      name: 'Custom Screens',
      icon: MagnifyingGlassIcon,
      description: 'Create and save custom stock filters'
    }
  ]

  const renderActiveComponent = () => {
    switch (activeTab) {
      case 'comparison':
        return <CompanyComparison />
      case 'earnings':
        return <EarningsCalendar />
      case 'dividends':
        return <DividendTracker />
      case 'economic':
        return <EconomicIndicatorTracker />
      case 'screens':
        return <CustomScreens />
      default:
        return <CompanyComparison />
    }
  }

  return (
    <>
      <Head>
        <title>Advanced Features - Casablanca Insight</title>
        <meta name="description" content="Advanced investment tools for Moroccan markets including company comparison, earnings calendar, dividend tracker, and custom screens." />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg">
        <Header />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Advanced Investment Tools
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Professional-grade tools for retail and institutional investors
            </p>
          </div>

          {/* Feature Overview */}
          <div className="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-dark-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-dark-border">
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                  <ChartBarIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Fundamentals Comparison</h3>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Compare 2-3 Moroccan companies side-by-side with key metrics like Revenue, Net Income, ROE, P/E, and Debt/Equity.
              </p>
            </div>

            <div className="bg-white dark:bg-dark-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-dark-border">
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
                  <CalendarIcon className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Earnings Calendar</h3>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Track upcoming earnings releases with email and push alerts for companies in your watchlist.
              </p>
            </div>

            <div className="bg-white dark:bg-dark-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-dark-border">
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
                  <CurrencyDollarIcon className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Dividend Tracker</h3>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Monitor dividend events with ex-dates, payout dates, yields, and payout ratios. Filter by high dividend or consistent payers.
              </p>
            </div>

            <div className="bg-white dark:bg-dark-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-dark-border">
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                  <ChartPieIcon className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Economic Indicators</h3>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Track key macro indicators like policy rates, FX reserves, and inflation with AI-powered trend analysis.
              </p>
            </div>

            <div className="bg-white dark:bg-dark-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-dark-border">
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-red-100 dark:bg-red-900/20 rounded-lg">
                  <MagnifyingGlassIcon className="w-6 h-6 text-red-600 dark:text-red-400" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Custom Screens</h3>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Create and save custom stock filters like "P/E &lt; 15 and Dividend &gt; 3%" for value investing strategies.
              </p>
            </div>

            <div className="bg-gradient-to-br from-casablanca-blue to-blue-600 p-6 rounded-lg shadow-sm text-white">
              <h3 className="font-semibold mb-2">Pro Features</h3>
              <p className="text-sm text-blue-100">
                These tools are designed for serious investors who need comprehensive data and analysis for Moroccan markets.
              </p>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="mb-6">
            <div className="border-b border-gray-200 dark:border-dark-border">
              <nav className="-mb-px flex space-x-8 overflow-x-auto">
                {tabs.map((tab) => {
                  const Icon = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors ${
                        activeTab === tab.id
                          ? 'border-casablanca-blue text-casablanca-blue'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span>{tab.name}</span>
                    </button>
                  )
                })}
              </nav>
            </div>
          </div>

          {/* Active Component */}
          <div className="mb-8">
            {renderActiveComponent()}
          </div>

          {/* Additional Information */}
          <div className="bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              About These Tools
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-600 dark:text-gray-400">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">For Retail Investors</h4>
                <ul className="space-y-1">
                  <li>• Easy-to-use comparison tools</li>
                  <li>• Dividend tracking for income strategies</li>
                  <li>• Earnings alerts to stay informed</li>
                  <li>• Custom screens for value investing</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">For Professional Investors</h4>
                <ul className="space-y-1">
                  <li>• Comprehensive financial metrics</li>
                  <li>• Economic indicator analysis</li>
                  <li>• Advanced filtering capabilities</li>
                  <li>• Data export and integration</li>
                </ul>
              </div>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  )
} 