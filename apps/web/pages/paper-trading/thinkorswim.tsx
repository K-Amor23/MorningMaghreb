import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useUser } from '@/lib/useUser'
import { useRouter } from 'next/router'
import ThinkOrSwimStyleInterface from '@/components/paper-trading/ThinkOrSwimStyleInterface'
import Header from '@/components/Header'
import { 
  ClockIcon, 
  ChartBarIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'

export default function ThinkOrSwimPaperTrading() {
  const { user, loading } = useUser()
  const router = useRouter()
  const [showInfo, setShowInfo] = useState(false)

  // Check authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-casablanca-blue"></div>
      </div>
    )
  }

  if (!user) {
    router.push('/login?redirect=/paper-trading/thinkorswim')
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-casablanca-blue mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Redirecting to login...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>ThinkOrSwim-Style Paper Trading - Casablanca Insight</title>
        <meta name="description" content="Advanced paper trading platform with delayed market data for Moroccan stocks" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header />
        
        {/* Info Banner */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border-b border-blue-200 dark:border-blue-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <ChartBarIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                <div>
                  <h1 className="text-lg font-semibold text-blue-900 dark:text-blue-100">
                    ThinkOrSwim-Style Paper Trading
                  </h1>
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    Advanced trading interface with delayed market data
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowInfo(!showInfo)}
                className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
              >
                <InformationCircleIcon className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Info Panel */}
        {showInfo && (
          <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="flex items-start space-x-3">
                  <ClockIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                      Delayed Data
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Market data is delayed by 15 minutes, similar to Charles Schwab's ThinkOrSwim paper trading
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <ExclamationTriangleIcon className="h-5 w-5 text-orange-600 dark:text-orange-400 mt-0.5" />
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                      Paper Trading Only
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      This is a simulation environment. No real money is involved in trades
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <ChartBarIcon className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5" />
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                      Realistic Experience
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Practice trading with realistic market conditions and order types
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Trading Interface */}
        <ThinkOrSwimStyleInterface accountId="thinkorswim-account-1" />
      </div>
    </>
  )
} 