import React, { useState, useEffect } from 'react'
import { PlusIcon, TrashIcon, BellIcon, ClockIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'
import { checkPremiumAccess, isPremiumEnforced } from '@/lib/featureFlags'

interface Webhook {
  id: string
  name: string
  url: string
  events: string[]
  is_active: boolean
  last_delivery?: string
  delivery_count: number
  failure_count: number
  created_at: string
}

interface WebhookDelivery {
  id: string
  webhook_id: string
  event_type: string
  status: 'success' | 'failed' | 'pending'
  response_code?: number
  response_time_ms?: number
  created_at: string
}

interface WebhookManagerProps {
  userSubscriptionTier: string
}

export default function WebhookManager({ userSubscriptionTier }: WebhookManagerProps) {
  const [webhooks, setWebhooks] = useState<Webhook[]>([])
  const [deliveries, setDeliveries] = useState<WebhookDelivery[]>([])
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [selectedWebhook, setSelectedWebhook] = useState<string | null>(null)

  const [newWebhook, setNewWebhook] = useState({
    name: '',
    url: '',
    events: ['price_alert', 'earnings_release'],
    secret: ''
  })

  const availableEvents = [
    { value: 'price_alert', label: 'Price Alerts', description: 'When stock prices cross thresholds' },
    { value: 'earnings_release', label: 'Earnings Releases', description: 'When companies announce earnings' },
    { value: 'dividend_payment', label: 'Dividend Payments', description: 'When dividends are paid' },
    { value: 'corporate_action', label: 'Corporate Actions', description: 'Mergers, acquisitions, splits' },
    { value: 'macro_update', label: 'Macro Updates', description: 'Economic indicator releases' },
    { value: 'news_alert', label: 'News Alerts', description: 'Breaking financial news' }
  ]

  useEffect(() => {
    if (checkPremiumAccess(userSubscriptionTier)) {
      fetchWebhooks()
    }
  }, [userSubscriptionTier])

  const fetchWebhooks = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/webhooks', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setWebhooks(data)
      } else {
        toast.error('Failed to fetch webhooks')
      }
    } catch (error) {
      console.error('Error fetching webhooks:', error)
      toast.error('Failed to fetch webhooks')
    } finally {
      setLoading(false)
    }
  }

  const createWebhook = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/webhooks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        },
        body: JSON.stringify(newWebhook)
      })
      
      if (response.ok) {
        const webhook = await response.json()
        setWebhooks([webhook, ...webhooks])
        setShowCreateForm(false)
        setNewWebhook({
          name: '',
          url: '',
          events: ['price_alert', 'earnings_release'],
          secret: ''
        })
        toast.success('Webhook created successfully')
      } else {
        toast.error('Failed to create webhook')
      }
    } catch (error) {
      console.error('Error creating webhook:', error)
      toast.error('Failed to create webhook')
    } finally {
      setLoading(false)
    }
  }

  const deleteWebhook = async (webhookId: string) => {
    if (!confirm('Are you sure you want to delete this webhook? This action cannot be undone.')) {
      return
    }

    try {
      const response = await fetch(`/api/webhooks/${webhookId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })
      
      if (response.ok) {
        setWebhooks(webhooks.filter(webhook => webhook.id !== webhookId))
        toast.success('Webhook deleted successfully')
      } else {
        toast.error('Failed to delete webhook')
      }
    } catch (error) {
      console.error('Error deleting webhook:', error)
      toast.error('Failed to delete webhook')
    }
  }

  const toggleWebhook = async (webhookId: string, isActive: boolean) => {
    try {
      const response = await fetch(`/api/webhooks/${webhookId}/toggle`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        },
        body: JSON.stringify({ is_active: !isActive })
      })
      
      if (response.ok) {
        setWebhooks(webhooks.map(webhook => 
          webhook.id === webhookId 
            ? { ...webhook, is_active: !isActive }
            : webhook
        ))
        toast.success(`Webhook ${!isActive ? 'activated' : 'deactivated'} successfully`)
      } else {
        toast.error('Failed to toggle webhook')
      }
    } catch (error) {
      console.error('Error toggling webhook:', error)
      toast.error('Failed to toggle webhook')
    }
  }

  const testWebhook = async (webhookId: string) => {
    try {
      const response = await fetch(`/api/webhooks/${webhookId}/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })
      
      if (response.ok) {
        toast.success('Test webhook sent successfully')
      } else {
        toast.error('Failed to send test webhook')
      }
    } catch (error) {
      console.error('Error testing webhook:', error)
      toast.error('Failed to send test webhook')
    }
  }

  const fetchDeliveries = async (webhookId: string) => {
    try {
      const response = await fetch(`/api/webhooks/${webhookId}/deliveries`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setDeliveries(data)
        setSelectedWebhook(webhookId)
      }
    } catch (error) {
      console.error('Error fetching deliveries:', error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircleIcon className="h-4 w-4 text-red-500" />
      case 'pending':
        return <ClockIcon className="h-4 w-4 text-yellow-500" />
      default:
        return <ClockIcon className="h-4 w-4 text-gray-500" />
    }
  }

  if (!checkPremiumAccess(userSubscriptionTier)) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              {isPremiumEnforced() ? 'Institutional Tier Required' : 'Feature Disabled'}
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>
                {isPremiumEnforced() 
                  ? 'Webhook management is available for institutional tier subscribers. Upgrade your subscription to access this feature.'
                  : 'Webhook management is currently disabled. Contact support for access.'
                }
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Webhook Management</h2>
          <p className="text-sm text-gray-600">
            Set up real-time data delivery via webhooks for automated notifications
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Create Webhook
        </button>
      </div>

      {/* Create Webhook Form */}
      {showCreateForm && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Webhook</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Webhook Name
              </label>
              <input
                type="text"
                value={newWebhook.name}
                onChange={(e) => setNewWebhook({...newWebhook, name: e.target.value})}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Price Alerts for ATW"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Webhook URL
              </label>
              <input
                type="url"
                value={newWebhook.url}
                onChange={(e) => setNewWebhook({...newWebhook, url: e.target.value})}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="https://your-server.com/webhook"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Secret Key (Optional)
              </label>
              <input
                type="text"
                value={newWebhook.secret}
                onChange={(e) => setNewWebhook({...newWebhook, secret: e.target.value})}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Secret key for webhook verification"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Events to Subscribe
              </label>
              <div className="mt-2 space-y-2">
                {availableEvents.map((event) => (
                  <label key={event.value} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={newWebhook.events.includes(event.value)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setNewWebhook({
                            ...newWebhook,
                            events: [...newWebhook.events, event.value]
                          })
                        } else {
                          setNewWebhook({
                            ...newWebhook,
                            events: newWebhook.events.filter(evt => evt !== event.value)
                          })
                        }
                      }}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <div className="ml-3">
                      <div className="text-sm font-medium text-gray-900">{event.label}</div>
                      <div className="text-sm text-gray-500">{event.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                onClick={createWebhook}
                disabled={loading || !newWebhook.name || !newWebhook.url}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Webhook'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Webhooks List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {webhooks.map((webhook) => (
            <li key={webhook.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <BellIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center">
                        <p className="text-sm font-medium text-gray-900">{webhook.name}</p>
                        <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          webhook.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {webhook.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500">{webhook.url}</p>
                      <div className="mt-1 flex items-center space-x-2">
                        <span className="text-xs text-gray-500">
                          {webhook.events.length} events • {webhook.delivery_count} deliveries
                        </span>
                        {webhook.failure_count > 0 && (
                          <span className="text-xs text-red-500">
                            {webhook.failure_count} failures
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => testWebhook(webhook.id)}
                      className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                    >
                      Test
                    </button>
                    <button
                      onClick={() => toggleWebhook(webhook.id, webhook.is_active)}
                      className={`text-sm font-medium ${
                        webhook.is_active 
                          ? 'text-yellow-600 hover:text-yellow-900' 
                          : 'text-green-600 hover:text-green-900'
                      }`}
                    >
                      {webhook.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button
                      onClick={() => fetchDeliveries(webhook.id)}
                      className="text-gray-600 hover:text-gray-900 text-sm font-medium"
                    >
                      History
                    </button>
                    <button
                      onClick={() => deleteWebhook(webhook.id)}
                      className="text-red-600 hover:text-red-900 text-sm font-medium"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Delivery History Modal */}
      {selectedWebhook && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Delivery History</h3>
              <div className="max-h-96 overflow-y-auto">
                <div className="space-y-2">
                  {deliveries.map((delivery) => (
                    <div key={delivery.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(delivery.status)}
                        <div>
                          <p className="text-sm font-medium text-gray-900">{delivery.event_type}</p>
                          <p className="text-xs text-gray-500">{formatDate(delivery.created_at)}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className={`text-sm font-medium ${
                          delivery.status === 'success' ? 'text-green-600' :
                          delivery.status === 'failed' ? 'text-red-600' : 'text-yellow-600'
                        }`}>
                          {delivery.status}
                        </p>
                        {delivery.response_code && (
                          <p className="text-xs text-gray-500">Code: {delivery.response_code}</p>
                        )}
                        {delivery.response_time_ms && (
                          <p className="text-xs text-gray-500">{delivery.response_time_ms}ms</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => setSelectedWebhook(null)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 