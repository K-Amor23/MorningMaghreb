import { useState, useEffect } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useUser } from '@/lib/useUser'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import TradingAccountOverview from '@/components/paper-trading/TradingAccountOverview'
import TradingInterface from '@/components/paper-trading/TradingInterface'
import PortfolioPositions from '@/components/paper-trading/PortfolioPositions'
import OrderHistory from '@/components/paper-trading/OrderHistory'
import TradingPerformance from '@/components/paper-trading/TradingPerformance'

interface TradingAccount {
  id: string
  user_id: string
  account_name: string
  initial_balance: number
  current_balance: number
  total_pnl: number
  total_pnl_percent: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export default function PaperTrading() {
  const { user, loading } = useUser()
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedAccount, setSelectedAccount] = useState<TradingAccount | null>(null)
  const [accounts, setAccounts] = useState<TradingAccount[]>([])
  const [loadingAccounts, setLoadingAccounts] = useState(true)

  useEffect(() => {
    if (user) {
      fetchTradingAccounts()
    }
  }, [user])

  const fetchTradingAccounts = async () => {
    try {
      const response = await fetch('/api/paper-trading/accounts', {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setAccounts(data)
        if (data.length > 0 && !selectedAccount) {
          setSelectedAccount(data[0])
        }
      } else {
        // If no accounts exist, create a default one
        await createDefaultAccount()
      }
    } catch (error) {
      console.error('Error fetching trading accounts:', error)
    } finally {
      setLoadingAccounts(false)
    }
  }

  const createDefaultAccount = async () => {
    try {
      const response = await fetch('/api/paper-trading/accounts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          account_name: 'My Paper Trading Account',
          initial_balance: 100000
        })
      })
      
      if (response.ok) {
        const newAccount = await response.json()
        setAccounts([newAccount])
        setSelectedAccount(newAccount)
      }
    } catch (error) {
      console.error('Error creating trading account:', error)
    }
  }

  const tabs = [
    { id: 'overview', name: 'Account Overview', icon: '📊' },
    { id: 'trade', name: 'Trade', icon: '💹' },
    { id: 'positions', name: 'Positions', icon: '📈' },
    { id: 'orders', name: 'Order History', icon: '📋' },
    { id: 'performance', name: 'Performance', icon: '📊' }
  ]

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-casablanca-blue"></div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Access Required
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Please log in to access the paper trading simulator.
          </p>
          <Link
            href="/login"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-casablanca-blue hover:bg-blue-700"
          >
            Sign In
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Head>
        <title>Paper Trading Simulator - Casablanca Insight</title>
        <meta name="description" content="Practice trading Moroccan stocks with our paper trading simulator" />
      </Head>

      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                📈 Paper Trading Simulator
              </h1>
              <p className="text-lg text-gray-600 dark:text-gray-400">
                Practice trading Moroccan stocks with virtual money
              </p>
            </div>
            
            {/* Account Selector */}
            {accounts.length > 0 && (
              <div className="flex items-center space-x-4">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Trading Account:
                </label>
                <select
                  value={selectedAccount?.id || ''}
                  onChange={(e) => {
                    const account = accounts.find(acc => acc.id === e.target.value)
                    setSelectedAccount(account || null)
                  }}
                  className="block w-64 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-casablanca-blue focus:ring-casablanca-blue sm:text-sm"
                >
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>
                      {account.account_name} - {account.current_balance.toLocaleString()} MAD
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>

        {/* Warning Banner */}
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-8">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                Paper Trading Disclaimer
              </h3>
              <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                <p>
                  This is a paper trading simulator for educational purposes only. 
                  No real money is involved. Past performance does not guarantee future results. 
                  Always do your own research before making real investment decisions.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loadingAccounts ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-casablanca-blue"></div>
          </div>
        ) : (
          <>
            {/* Tab Navigation */}
            <div className="border-b border-gray-200 dark:border-gray-700 mb-8">
              <nav className="-mb-px flex space-x-8">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      py-2 px-1 border-b-2 font-medium text-sm
                      ${activeTab === tab.id
                        ? 'border-casablanca-blue text-casablanca-blue'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                      }
                    `}
                  >
                    <span className="mr-2">{tab.icon}</span>
                    {tab.name}
                  </button>
                ))}
              </nav>
            </div>

            {/* Tab Content */}
            <div className="space-y-8">
              {activeTab === 'overview' && selectedAccount && (
                <TradingAccountOverview accountId={selectedAccount.id} />
              )}
              
              {activeTab === 'trade' && selectedAccount && (
                <TradingInterface accountId={selectedAccount.id} />
              )}
              
              {activeTab === 'positions' && selectedAccount && (
                <PortfolioPositions accountId={selectedAccount.id} />
              )}
              
              {activeTab === 'orders' && selectedAccount && (
                <OrderHistory accountId={selectedAccount.id} />
              )}
              
              {activeTab === 'performance' && selectedAccount && (
                <TradingPerformance accountId={selectedAccount.id} />
              )}
            </div>
          </>
        )}
      </main>

      <Footer />
    </div>
  )
} 