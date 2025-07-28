import { useState, useEffect } from 'react'
import { BellIcon, PlusIcon, TrashIcon, PauseIcon, PlayIcon } from '@heroicons/react/24/outline'
import { PriceAlert, CreatePriceAlertData, createPriceAlert, getUserPriceAlerts, deletePriceAlert, updatePriceAlert } from '@/lib/priceAlerts'
import { MarketQuote } from '@/lib/supabase'
import toast from 'react-hot-toast'

interface PriceAlertsProps {
  userId: string
  marketData: MarketQuote[]
}

export default function PriceAlerts({ userId, marketData }: PriceAlertsProps) {
  const [alerts, setAlerts] = useState<PriceAlert[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newAlert, setNewAlert] = useState<CreatePriceAlertData>({
    symbol: '',
    condition: 'above',
    target_price: 0
  })

  const fetchAlerts = async () => {
    try {
      const userAlerts = await getUserPriceAlerts()
      setAlerts(userAlerts)
    } catch (error) {
      console.error('Error fetching alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
  }, [userId])

  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!newAlert.symbol || newAlert.target_price <= 0) {
      toast.error('Please fill in all fields correctly')
      return
    }

    const createdAlert = await createPriceAlert(newAlert)
    if (createdAlert) {
      setAlerts(prev => [createdAlert, ...prev])
      setNewAlert({ symbol: '', condition: 'above', target_price: 0 })
      setShowCreateForm(false)
    }
  }

  const handleDeleteAlert = async (alertId: string) => {
    const success = await deletePriceAlert(alertId)
    if (success) {
      setAlerts(prev => prev.filter(alert => alert.id !== alertId))
    }
  }

  const handleToggleAlert = async (alert: PriceAlert) => {
    const success = await updatePriceAlert(alert.id, { is_active: !alert.is_active })
    if (success) {
      setAlerts(prev => prev.map(a =>
        a.id === alert.id ? { ...a, is_active: !a.is_active } : a
      ))
    }
  }

  const getCurrentPrice = (symbol: string): number | null => {
    const marketItem = marketData.find(item => item.symbol === symbol)
    return marketItem ? marketItem.price : null
  }

  const getAlertStatus = (alert: PriceAlert): 'active' | 'triggered' | 'inactive' => {
    if (alert.triggered_at) return 'triggered'
    if (alert.is_active) return 'active'
    return 'inactive'
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100'
      case 'triggered': return 'text-red-600 bg-red-100'
      case 'inactive': return 'text-gray-600 bg-gray-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-12 bg-gray-200 rounded"></div>
            <div className="h-12 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <BellIcon className="h-5 w-5 text-gray-400 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">
              Price Alerts
            </h3>
          </div>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-casablanca-blue hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-casablanca-blue"
          >
            <PlusIcon className="h-4 w-4 mr-1" />
            Add Alert
          </button>
        </div>
      </div>

      {showCreateForm && (
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <form onSubmit={handleCreateAlert} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Ticker
                </label>
                <input
                  type="text"
                  value={newAlert.symbol}
                  onChange={(e) => setNewAlert(prev => ({ ...prev, symbol: e.target.value.toUpperCase() }))}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-casablanca-blue focus:border-casablanca-blue sm:text-sm"
                  placeholder="e.g., IAM"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Alert Type
                </label>
                <select
                  value={newAlert.condition}
                  onChange={(e) => setNewAlert(prev => ({ ...prev, condition: e.target.value as 'above' | 'below' }))}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-casablanca-blue focus:border-casablanca-blue sm:text-sm"
                >
                  <option value="above">Above</option>
                  <option value="below">Below</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Price Threshold
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={newAlert.target_price}
                  onChange={(e) => setNewAlert(prev => ({ ...prev, target_price: parseFloat(e.target.value) || 0 }))}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-casablanca-blue focus:border-casablanca-blue sm:text-sm"
                  placeholder="0.00"
                  required
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-casablanca-blue"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-casablanca-blue hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-casablanca-blue"
              >
                Create Alert
              </button>
            </div>
          </form>
        </div>
      )}

      {alerts.length === 0 ? (
        <div className="px-6 py-8 text-center">
          <BellIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No price alerts</h3>
          <p className="mt-1 text-sm text-gray-500">
            Create price alerts to get notified when stocks reach your target prices.
          </p>
        </div>
      ) : (
        <div className="divide-y divide-gray-200">
          {alerts.map((alert) => {
            const currentPrice = getCurrentPrice(alert.symbol)
            const status = getAlertStatus(alert)

            return (
              <div key={alert.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">
                          {alert.symbol}
                        </h4>
                        <div className="mt-1 flex items-center space-x-4 text-sm">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                            {status === 'active' && 'Active'}
                            {status === 'triggered' && 'Triggered'}
                            {status === 'inactive' && 'Paused'}
                          </span>
                          <span className="text-gray-600">
                            {alert.condition === 'above' ? 'Above' : 'Below'} {alert.target_price.toFixed(2)}
                          </span>
                          {currentPrice && (
                            <span className="text-gray-900 font-medium">
                              Current: {currentPrice.toFixed(2)}
                            </span>
                          )}
                        </div>
                        {alert.triggered_at && (
                          <p className="mt-1 text-xs text-gray-500">
                            Triggered on {new Date(alert.triggered_at).toLocaleDateString()}
                          </p>
                        )}
                      </div>

                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleToggleAlert(alert)}
                          className="p-1 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 rounded"
                          title={alert.is_active ? 'Pause alert' : 'Activate alert'}
                        >
                          {alert.is_active ? (
                            <PauseIcon className="h-4 w-4" />
                          ) : (
                            <PlayIcon className="h-4 w-4" />
                          )}
                        </button>

                        <button
                          onClick={() => handleDeleteAlert(alert.id)}
                          className="p-1 text-gray-400 hover:text-red-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 rounded"
                          title="Delete alert"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
} 