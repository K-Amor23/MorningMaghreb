import React, { useState, useEffect } from 'react'
import { 
  ExclamationTriangleIcon,
  PauseIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  InformationCircleIcon,
  ShieldCheckIcon,
  ClockIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

interface TradingHalt {
  id: string
  ticker: string
  halt_type: string
  halt_reason: string
  halt_start: string
  halt_end?: string
  price_at_halt?: number
  is_active: boolean
}

interface RuleViolation {
  id: string
  ticker: string
  violation_type: string
  violation_details?: any
  price_at_violation?: number
  violation_timestamp: string
  status: string
}

interface PriceAlert {
  id: string
  ticker: string
  alert_type: string
  current_price: number
  price_change_percent?: number
  threshold_percent?: number
  alert_message?: string
  is_triggered: boolean
  triggered_at?: string
}

interface ComplianceSummary {
  active_halts: TradingHalt[]
  recent_violations: RuleViolation[]
  price_alerts: PriceAlert[]
  total_violations_today: number
  total_halts_today: number
  stocks_nearing_limits: string[]
}

interface ComplianceDashboardProps {
  userId: string
}

export default function ComplianceDashboard({ userId }: ComplianceDashboardProps) {
  const [summary, setSummary] = useState<ComplianceSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'halts' | 'violations' | 'alerts' | 'education'>('overview')

  useEffect(() => {
    fetchComplianceSummary()
  }, [userId])

  const fetchComplianceSummary = async () => {
    try {
      setLoading(true)
      // In production, this would be a real API call
      const mockSummary: ComplianceSummary = {
        active_halts: [
          {
            id: '1',
            ticker: 'ATW',
            halt_type: 'circuit_breaker',
            halt_reason: 'Price dropped 16.5% - circuit breaker triggered',
            halt_start: new Date().toISOString(),
            price_at_halt: 45.20,
            is_active: true
          }
        ],
        recent_violations: [
          {
            id: '1',
            ticker: 'IAM',
            violation_type: 'price_limit_exceeded',
            price_at_violation: 12.50,
            violation_timestamp: new Date().toISOString(),
            status: 'active'
          }
        ],
        price_alerts: [
          {
            id: '1',
            ticker: 'BCP',
            alert_type: 'approaching_limit',
            current_price: 28.75,
            price_change_percent: 8.5,
            threshold_percent: 10.0,
            alert_message: 'Price approaching daily limit',
            is_triggered: true,
            triggered_at: new Date().toISOString()
          }
        ],
        total_violations_today: 3,
        total_halts_today: 1,
        stocks_nearing_limits: ['ATW', 'IAM', 'BCP']
      }
      
      setSummary(mockSummary)
    } catch (error) {
      console.error('Error fetching compliance summary:', error)
    } finally {
      setLoading(false)
    }
  }

  const getHaltTypeIcon = (type: string) => {
    switch (type) {
      case 'circuit_breaker':
        return <ArrowTrendingDownIcon className="w-4 h-4" />
      case 'news_pending':
        return <InformationCircleIcon className="w-4 h-4" />
      case 'regulatory':
        return <ShieldCheckIcon className="w-4 h-4" />
      default:
        return <PauseIcon className="w-4 h-4" />
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            CSE Compliance Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Monitor trading rules, halts, and compliance violations
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: ChartBarIcon },
              { id: 'halts', label: 'Trading Halts', icon: PauseIcon },
              { id: 'violations', label: 'Violations', icon: ExclamationTriangleIcon },
              { id: 'alerts', label: 'Price Alerts', icon: ArrowTrendingUpIcon },
              { id: 'education', label: 'Education', icon: InformationCircleIcon }
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <OverviewTab summary={summary} getHaltTypeIcon={getHaltTypeIcon} />
          )}
          
          {activeTab === 'halts' && (
            <HaltsTab halts={summary?.active_halts || []} getHaltTypeIcon={getHaltTypeIcon} />
          )}
          
          {activeTab === 'violations' && (
            <ViolationsTab violations={summary?.recent_violations || []} />
          )}
          
          {activeTab === 'alerts' && (
            <AlertsTab alerts={summary?.price_alerts || []} />
          )}
          
          {activeTab === 'education' && (
            <EducationTab />
          )}
        </div>
      </div>
    </div>
  )
}

function OverviewTab({ 
  summary, 
  getHaltTypeIcon 
}: { 
  summary: ComplianceSummary | null
  getHaltTypeIcon: (type: string) => JSX.Element
}) {
  if (!summary) return null

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 dark:bg-red-900/20 rounded-lg">
              <PauseIcon className="w-6 h-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Halts</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.active_halts.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
              <ExclamationTriangleIcon className="w-6 h-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Violations Today</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.total_violations_today}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
              <ArrowTrendingUpIcon className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Price Alerts</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.price_alerts.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <ChartBarIcon className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Near Limits</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.stocks_nearing_limits.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Active Halts */}
      {summary.active_halts.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Active Trading Halts</h3>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {summary.active_halts.map((halt) => (
              <div key={halt.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getHaltTypeIcon(halt.halt_type)}
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{halt.ticker}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{halt.halt_reason}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Since {new Date(halt.halt_start).toLocaleTimeString()}
                    </p>
                    {halt.price_at_halt && (
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        Price: {halt.price_at_halt.toFixed(2)} MAD
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stocks Nearing Limits */}
      {summary.stocks_nearing_limits.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Stocks Nearing Daily Limits</h3>
          </div>
          <div className="px-6 py-4">
            <div className="flex flex-wrap gap-2">
              {summary.stocks_nearing_limits.map((ticker) => (
                <span
                  key={ticker}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400"
                >
                  <ArrowTrendingUpIcon className="w-4 h-4 mr-1" />
                  {ticker}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function HaltsTab({ 
  halts, 
  getHaltTypeIcon 
}: { 
  halts: TradingHalt[]
  getHaltTypeIcon: (type: string) => JSX.Element
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">Trading Halts</h3>
      </div>
      {halts.length === 0 ? (
        <div className="px-6 py-8 text-center">
          <PauseIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">No active trading halts</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {halts.map((halt) => (
            <div key={halt.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getHaltTypeIcon(halt.halt_type)}
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{halt.ticker}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{halt.halt_reason}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {new Date(halt.halt_start).toLocaleString()}
                  </p>
                  {halt.price_at_halt && (
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {halt.price_at_halt.toFixed(2)} MAD
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function ViolationsTab({ violations }: { violations: RuleViolation[] }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">Recent Violations</h3>
      </div>
      {violations.length === 0 ? (
        <div className="px-6 py-8 text-center">
          <ShieldCheckIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">No recent violations</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {violations.map((violation) => (
            <div key={violation.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <ExclamationTriangleIcon className="w-5 h-5 text-orange-600" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{violation.ticker}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{violation.violation_type}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {new Date(violation.violation_timestamp).toLocaleString()}
                  </p>
                  {violation.price_at_violation && (
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {violation.price_at_violation.toFixed(2)} MAD
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function AlertsTab({ alerts }: { alerts: PriceAlert[] }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">Price Movement Alerts</h3>
      </div>
      {alerts.length === 0 ? (
        <div className="px-6 py-8 text-center">
          <ArrowTrendingUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">No price alerts</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {alerts.map((alert) => (
            <div key={alert.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <ArrowTrendingUpIcon className="w-5 h-5 text-yellow-600" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{alert.ticker}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{alert.alert_message}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {alert.triggered_at && new Date(alert.triggered_at).toLocaleString()}
                  </p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {alert.current_price.toFixed(2)} MAD
                  </p>
                  {alert.price_change_percent && (
                    <p className={`text-sm font-medium ${
                      alert.price_change_percent > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {alert.price_change_percent > 0 ? '+' : ''}{alert.price_change_percent.toFixed(2)}%
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function EducationTab() {
  return (
    <div className="space-y-6">
      {/* Circuit Breakers */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Circuit Breakers</h3>
        </div>
        <div className="px-6 py-4">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Circuit breakers are automatic trading halts triggered by significant price movements to prevent market panic.
          </p>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-sm font-medium">15% drop:</span>
              <span className="text-sm text-gray-600 dark:text-gray-400">15-minute trading halt</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-red-600 rounded-full"></div>
              <span className="text-sm font-medium">20% drop:</span>
              <span className="text-sm text-gray-600 dark:text-gray-400">30-minute trading halt</span>
            </div>
          </div>
        </div>
      </div>

      {/* Daily Price Limits */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Daily Price Limits</h3>
        </div>
        <div className="px-6 py-4">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Daily price limits prevent excessive volatility by restricting maximum price movement in a single day.
          </p>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-sm font-medium">Standard stocks:</span>
              <span className="text-sm text-gray-600 dark:text-gray-400">±10% daily limit</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium">New listings:</span>
              <span className="text-sm text-gray-600 dark:text-gray-400">±20% daily limit (first 30 days)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Trading Rules */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">CSE Trading Rules</h3>
        </div>
        <div className="px-6 py-4">
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Order Types</h4>
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Market orders: Immediate execution at current price</li>
                <li>• Limit orders: Execution at specified price or better</li>
                <li>• Stop orders: Triggered when price reaches specified level</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Trading Hours</h4>
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Pre-market: 9:00 AM - 9:30 AM</li>
                <li>• Regular trading: 9:30 AM - 3:30 PM</li>
                <li>• Post-market: 3:30 PM - 4:00 PM</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 