import React, { useState, useEffect } from 'react'
import { PlusIcon, TrashIcon, EyeIcon, EyeSlashIcon, ClipboardIcon } from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'
import { checkPremiumAccess, isPremiumEnforced } from '@/lib/featureFlags'

interface ApiKey {
  id: string
  key_name: string
  permissions: string[]
  is_active: boolean
  last_used?: string
  created_at: string
  api_key?: string // Only shown on creation
}

interface ApiKeyManagerProps {
  userSubscriptionTier: string
}

export default function ApiKeyManager({ userSubscriptionTier }: ApiKeyManagerProps) {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showApiKey, setShowApiKey] = useState<string | null>(null)

  const [newKeyData, setNewKeyData] = useState({
    key_name: '',
    permissions: ['read_financials', 'read_macro', 'read_quotes'],
    rate_limit_per_hour: 1000,
    expires_in_days: 365
  })

  const availablePermissions = [
    { value: 'read_financials', label: 'Financial Data' },
    { value: 'read_macro', label: 'Macro Data' },
    { value: 'read_quotes', label: 'Market Quotes' },
    { value: 'read_portfolio', label: 'Portfolio Data' },
    { value: 'read_reports', label: 'Custom Reports' }
  ]

  useEffect(() => {
    if (checkPremiumAccess('PREMIUM_FEATURES')) {
      fetchApiKeys()
    }
  }, [userSubscriptionTier])

  const fetchApiKeys = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/premium/api-keys', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setApiKeys(data)
      } else {
        toast.error('Failed to fetch API keys')
      }
    } catch (error) {
      console.error('Error fetching API keys:', error)
      toast.error('Failed to fetch API keys')
    } finally {
      setLoading(false)
    }
  }

  const createApiKey = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/premium/api-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        },
        body: JSON.stringify(newKeyData)
      })

      if (response.ok) {
        const newKey = await response.json()
        setApiKeys([newKey, ...apiKeys])
        setShowCreateForm(false)
        setNewKeyData({
          key_name: '',
          permissions: ['read_financials', 'read_macro', 'read_quotes'],
          rate_limit_per_hour: 1000,
          expires_in_days: 365
        })
        toast.success('API key created successfully')
      } else {
        toast.error('Failed to create API key')
      }
    } catch (error) {
      console.error('Error creating API key:', error)
      toast.error('Failed to create API key')
    } finally {
      setLoading(false)
    }
  }

  const deleteApiKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return
    }

    try {
      const response = await fetch(`/api/premium/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`
        }
      })

      if (response.ok) {
        setApiKeys(apiKeys.filter(key => key.id !== keyId))
        toast.success('API key deleted successfully')
      } else {
        toast.error('Failed to delete API key')
      }
    } catch (error) {
      console.error('Error deleting API key:', error)
      toast.error('Failed to delete API key')
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard')
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

  if (!checkPremiumAccess('PREMIUM_FEATURES')) {
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
                  ? 'API key management is available for institutional tier subscribers. Upgrade your subscription to access this feature.'
                  : 'API key management is currently disabled. Contact support for access.'
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
          <h2 className="text-lg font-semibold text-gray-900">API Keys</h2>
          <p className="text-sm text-gray-600">
            Manage your API keys for programmatic access to Casablanca Insights data
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Create API Key
        </button>
      </div>

      {/* Create API Key Form */}
      {showCreateForm && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Create New API Key</h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Key Name
              </label>
              <input
                type="text"
                value={newKeyData.key_name}
                onChange={(e) => setNewKeyData({ ...newKeyData, key_name: e.target.value })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="e.g., Production API Key"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Permissions
              </label>
              <div className="space-y-2">
                {availablePermissions.map((permission) => (
                  <label key={permission.value} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={newKeyData.permissions.includes(permission.value)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setNewKeyData({
                            ...newKeyData,
                            permissions: [...newKeyData.permissions, permission.value]
                          })
                        } else {
                          setNewKeyData({
                            ...newKeyData,
                            permissions: newKeyData.permissions.filter(p => p !== permission.value)
                          })
                        }
                      }}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">{permission.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Rate Limit (per hour)
                </label>
                <input
                  type="number"
                  value={newKeyData.rate_limit_per_hour}
                  onChange={(e) => setNewKeyData({ ...newKeyData, rate_limit_per_hour: parseInt(e.target.value) })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  min="1"
                  max="10000"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Expires in (days)
                </label>
                <input
                  type="number"
                  value={newKeyData.expires_in_days}
                  onChange={(e) => setNewKeyData({ ...newKeyData, expires_in_days: parseInt(e.target.value) })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  min="1"
                  max="3650"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                onClick={createApiKey}
                disabled={loading || !newKeyData.key_name}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create API Key'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* API Keys List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        {loading ? (
          <div className="p-6 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Loading API keys...</p>
          </div>
        ) : apiKeys.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-sm text-gray-600">No API keys found. Create your first API key to get started.</p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {apiKeys.map((apiKey) => (
              <li key={apiKey.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">{apiKey.key_name}</h3>
                        <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                          <span>Created: {formatDate(apiKey.created_at)}</span>
                          {apiKey.last_used && (
                            <span>Last used: {formatDate(apiKey.last_used)}</span>
                          )}
                        </div>
                        <div className="mt-2 flex flex-wrap gap-1">
                          {apiKey.permissions.map((permission) => (
                            <span
                              key={permission}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                            >
                              {permission.replace('read_', '')}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${apiKey.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                          }`}>
                          {apiKey.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </div>

                    {/* Show API key if just created */}
                    {apiKey.api_key && (
                      <div className="mt-3 p-3 bg-gray-50 rounded-md">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="text-xs font-medium text-gray-700 mb-1">API Key (save this securely)</p>
                            <div className="flex items-center space-x-2">
                              <code className="text-sm bg-white px-2 py-1 rounded border flex-1">
                                {showApiKey === apiKey.id ? apiKey.api_key : '••••••••••••••••••••••••••••••••'}
                              </code>
                              <button
                                onClick={() => setShowApiKey(showApiKey === apiKey.id ? null : apiKey.id)}
                                className="text-gray-400 hover:text-gray-600"
                              >
                                {showApiKey === apiKey.id ? (
                                  <EyeSlashIcon className="h-4 w-4" />
                                ) : (
                                  <EyeIcon className="h-4 w-4" />
                                )}
                              </button>
                              <button
                                onClick={() => copyToClipboard(apiKey.api_key!)}
                                className="text-gray-400 hover:text-gray-600"
                              >
                                <ClipboardIcon className="h-4 w-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="ml-4 flex-shrink-0">
                    <button
                      onClick={() => deleteApiKey(apiKey.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Usage Information */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800 mb-2">API Key Usage</h3>
        <div className="text-sm text-blue-700 space-y-1">
          <p>• Include your API key in the <code className="bg-blue-100 px-1 rounded">X-API-Key</code> header</p>
          <p>• Rate limits apply per API key</p>
          <p>• Keep your API keys secure and never share them publicly</p>
          <p>• You can revoke keys at any time by deleting them</p>
        </div>
      </div>
    </div>
  )
} 