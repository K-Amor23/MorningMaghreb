import React, { useState, useEffect } from 'react'
import { BellIcon, PlusIcon, TrashIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { useLocalStorageGetter } from '@/lib/useClientOnly'

interface Webhook {
  id: string
  name: string
  url: string
  events: string[]
  is_active: boolean
  created_at: string
  last_triggered?: string
  secret_key?: string
}

export default function WebhookManager() {
  const [webhooks, setWebhooks] = useState<Webhook[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newWebhook, setNewWebhook] = useState({
    name: '',
    url: '',
    events: [] as string[]
  })
  const [showSecret, setShowSecret] = useState<string | null>(null)
  const { getItem, mounted } = useLocalStorageGetter()

  const availableEvents = [
    'price_alert',
    'portfolio_change',
    'market_open',
    'market_close',
    'earnings_release',
    'dividend_payment'
  ]

  useEffect(() => {
    if (mounted) {
      fetchWebhooks()
    }
  }, [mounted])

  const fetchWebhooks = async () => {
    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch('/api/premium/webhooks', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setWebhooks(data.webhooks || [])
      }
    } catch (error) {
      console.error('Error fetching webhooks:', error)
    } finally {
      setLoading(false)
    }
  }

  const createWebhook = async () => {
    if (!newWebhook.name.trim() || !newWebhook.url.trim()) return

    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch('/api/premium/webhooks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newWebhook)
      })

      if (response.ok) {
        const data = await response.json()
        setWebhooks(prev => [...prev, data.webhook])
        setShowCreateForm(false)
        setNewWebhook({ name: '', url: '', events: [] })
      }
    } catch (error) {
      console.error('Error creating webhook:', error)
    }
  }

  const deleteWebhook = async (webhookId: string) => {
    if (!confirm('Are you sure you want to delete this webhook?')) return

    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch(`/api/premium/webhooks/${webhookId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setWebhooks(prev => prev.filter(webhook => webhook.id !== webhookId))
      }
    } catch (error) {
      console.error('Error deleting webhook:', error)
    }
  }

  const toggleEvent = (event: string) => {
    setNewWebhook(prev => ({
      ...prev,
      events: prev.events.includes(event)
        ? prev.events.filter(e => e !== event)
        : [...prev.events, event]
    }))
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

  if (!mounted) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-6"></div>
          <div className="space-y-3">
            <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Webhook Manager
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Manage webhooks for real-time notifications
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
        >
          <PlusIcon className="h-4 w-4" />
          <span>New Webhook</span>
        </button>
      </div>

      {showCreateForm && (
        <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Create New Webhook
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Webhook Name
              </label>
              <input
                type="text"
                value={newWebhook.name}
                onChange={(e) => setNewWebhook(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Price Alerts, Portfolio Updates"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Webhook URL
              </label>
              <input
                type="url"
                value={newWebhook.url}
                onChange={(e) => setNewWebhook(prev => ({ ...prev, url: e.target.value }))}
                placeholder="https://your-domain.com/webhook"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Events to Listen For
              </label>
              <div className="grid grid-cols-2 gap-2">
                {availableEvents.map(event => (
                  <label key={event} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={newWebhook.events.includes(event)}
                      onChange={() => toggleEvent(event)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {event.replace('_', ' ')}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={createWebhook}
                disabled={!newWebhook.name.trim() || !newWebhook.url.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
              >
                Create Webhook
              </button>
              <button
                onClick={() => {
                  setShowCreateForm(false)
                  setNewWebhook({ name: '', url: '', events: [] })
                }}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse">
              <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {webhooks.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <BellIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No webhooks configured yet</p>
              <p className="text-sm mt-1">Create your first webhook to get started</p>
            </div>
          ) : (
            webhooks.map(webhook => (
              <div key={webhook.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {webhook.name}
                      </h3>
                      <span className={`px-2 py-1 text-xs rounded-full ${webhook.is_active
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                        {webhook.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>

                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {webhook.url}
                    </div>

                    <div className="flex flex-wrap gap-1 mb-2">
                      {webhook.events.map(event => (
                        <span
                          key={event}
                          className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                        >
                          {event.replace('_', ' ')}
                        </span>
                      ))}
                    </div>

                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Created: {formatDate(webhook.created_at)}
                      {webhook.last_triggered && ` • Last triggered: ${formatDate(webhook.last_triggered)}`}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    {webhook.secret_key && (
                      <button
                        onClick={() => setShowSecret(showSecret === webhook.id ? null : webhook.id)}
                        className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                      >
                        {showSecret === webhook.id ? (
                          <EyeSlashIcon className="h-4 w-4" />
                        ) : (
                          <EyeIcon className="h-4 w-4" />
                        )}
                      </button>
                    )}
                    <button
                      onClick={() => deleteWebhook(webhook.id)}
                      className="text-red-600 hover:text-red-800 dark:text-red-400"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {showSecret === webhook.id && webhook.secret_key && (
                  <div className="mt-2 p-2 bg-gray-100 dark:bg-gray-700 rounded text-sm font-mono">
                    {webhook.secret_key}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
} 