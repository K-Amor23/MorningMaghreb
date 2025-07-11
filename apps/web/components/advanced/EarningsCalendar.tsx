'use client'

import { useState, useEffect } from 'react'
import { CalendarIcon, BellIcon, BellSlashIcon } from '@heroicons/react/24/outline'

interface EarningsEvent {
  company: string
  ticker: string
  earnings_date: string
  estimate?: number
  actual?: number
  surprise?: number
  sector: string
}

interface EarningsCalendarProps {
  className?: string
}

export default function EarningsCalendar({ className = '' }: EarningsCalendarProps) {
  const [earnings, setEarnings] = useState<EarningsEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([])
  const [dateRange, setDateRange] = useState({
    start: new Date().toISOString().split('T')[0],
    end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  })

  const availableCompanies = [
    { ticker: 'ATW', name: 'Attijariwafa Bank', sector: 'Banking' },
    { ticker: 'IAM', name: 'Maroc Telecom', sector: 'Telecommunications' },
    { ticker: 'BCP', name: 'Banque Centrale Populaire', sector: 'Banking' },
    { ticker: 'BMCE', name: 'BMCE Bank', sector: 'Banking' },
    { ticker: 'WAA', name: 'Wafa Assurance', sector: 'Insurance' },
    { ticker: 'CMA', name: 'Ciments du Maroc', sector: 'Construction Materials' }
  ]

  const fetchEarnings = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/advanced/earnings-calendar', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_date: dateRange.start,
          end_date: dateRange.end,
          companies: selectedCompanies.length > 0 ? selectedCompanies : undefined
        })
      })

      if (!response.ok) {
        throw new Error('Failed to fetch earnings calendar')
      }

      const data = await response.json()
      setEarnings(data)
    } catch (error) {
      console.error('Error fetching earnings:', error)
      // Fallback to mock data
      const mockEarnings: EarningsEvent[] = [
        {
          company: 'Attijariwafa Bank',
          ticker: 'ATW',
          earnings_date: '2024-11-15',
          estimate: 4.2,
          sector: 'Banking'
        },
        {
          company: 'Maroc Telecom',
          ticker: 'IAM',
          earnings_date: '2024-11-20',
          estimate: 1.8,
          sector: 'Telecommunications'
        },
        {
          company: 'Banque Centrale Populaire',
          ticker: 'BCP',
          earnings_date: '2024-11-25',
          estimate: 2.8,
          sector: 'Banking'
        },
        {
          company: 'BMCE Bank',
          ticker: 'BMCE',
          earnings_date: '2024-12-05',
          estimate: 1.5,
          sector: 'Banking'
        }
      ]
      setEarnings(mockEarnings)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEarnings()
  }, [dateRange, selectedCompanies])

  const toggleCompany = (ticker: string) => {
    if (selectedCompanies.includes(ticker)) {
      setSelectedCompanies(selectedCompanies.filter(c => c !== ticker))
    } else {
      setSelectedCompanies([...selectedCompanies, ticker])
    }
  }

  const toggleAlert = (ticker: string) => {
    // TODO: Implement actual alert toggle with backend
    console.log(`Toggle alert for ${ticker}`)
  }

  const getDaysUntilEarnings = (earningsDate: string) => {
    const today = new Date()
    const earnings = new Date(earningsDate)
    const diffTime = earnings.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    })
  }

  const getUrgencyColor = (daysUntil: number) => {
    if (daysUntil <= 3) return 'text-red-600 dark:text-red-400'
    if (daysUntil <= 7) return 'text-orange-600 dark:text-orange-400'
    if (daysUntil <= 14) return 'text-yellow-600 dark:text-yellow-400'
    return 'text-gray-600 dark:text-gray-400'
  }

  return (
    <div className={`bg-white dark:bg-dark-card rounded-lg shadow-sm border border-gray-200 dark:border-dark-border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Earnings Calendar
        </h2>
        <CalendarIcon className="w-6 h-6 text-gray-400" />
      </div>

      {/* Date Range Selection */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
          Date Range
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              className="w-full px-3 py-2 border border-gray-200 dark:border-dark-border rounded-lg text-sm bg-white dark:bg-dark-bg text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
              End Date
            </label>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              className="w-full px-3 py-2 border border-gray-200 dark:border-dark-border rounded-lg text-sm bg-white dark:bg-dark-bg text-gray-900 dark:text-white"
            />
          </div>
        </div>
      </div>

      {/* Company Filter */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
          Filter by Company
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {availableCompanies.map((company) => (
            <button
              key={company.ticker}
              onClick={() => toggleCompany(company.ticker)}
              className={`p-2 text-left rounded-lg border transition-colors ${
                selectedCompanies.includes(company.ticker)
                  ? 'border-casablanca-blue bg-casablanca-blue/10 text-casablanca-blue'
                  : 'border-gray-200 dark:border-dark-border hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <div className="font-medium text-xs">{company.ticker}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">{company.sector}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Earnings List */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-gray-900 dark:text-white">
          Upcoming Earnings ({earnings.length})
        </h3>
        
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-casablanca-blue"></div>
          </div>
        ) : earnings.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            No earnings scheduled in this date range
          </div>
        ) : (
          earnings.map((event) => {
            const daysUntil = getDaysUntilEarnings(event.earnings_date)
            const isAlertSet = false // TODO: Get from backend
            
            return (
              <div
                key={`${event.ticker}-${event.earnings_date}`}
                className="p-4 border border-gray-200 dark:border-dark-border rounded-lg hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <div>
                        <div className="font-medium text-gray-900 dark:text-white">
                          {event.company} ({event.ticker})
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {event.sector}
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-2 flex items-center space-x-4 text-sm">
                      <div className="flex items-center space-x-1">
                        <CalendarIcon className="w-4 h-4 text-gray-400" />
                        <span className={getUrgencyColor(daysUntil)}>
                          {formatDate(event.earnings_date)}
                        </span>
                      </div>
                      
                      <div className={`text-sm ${getUrgencyColor(daysUntil)}`}>
                        {daysUntil === 0 ? 'Today' : 
                         daysUntil < 0 ? `${Math.abs(daysUntil)} days ago` :
                         `${daysUntil} days`}
                      </div>
                      
                      {event.estimate && (
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          Est: {event.estimate.toFixed(2)} MAD
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => toggleAlert(event.ticker)}
                      className={`p-2 rounded-lg transition-colors ${
                        isAlertSet
                          ? 'bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-dark-hover dark:text-gray-400 dark:hover:bg-gray-700'
                      }`}
                      title={isAlertSet ? 'Remove alert' : 'Set alert'}
                    >
                      {isAlertSet ? (
                        <BellIcon className="w-4 h-4" />
                      ) : (
                        <BellSlashIcon className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* Alert Settings */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-dark-hover rounded-lg">
        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
          Alert Settings
        </h4>
        <p className="text-xs text-gray-600 dark:text-gray-400">
          Get email or push notifications for earnings releases. Click the bell icon next to any company to set alerts.
        </p>
      </div>
    </div>
  )
} 