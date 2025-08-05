import React, { useState, useEffect } from 'react'
import { KeyIcon, PlusIcon, TrashIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { useLocalStorageGetter } from '@/lib/useClientOnly'

interface ApiKey {
  id: string
  name: string
  key: string
  permissions: string[]
  created_at: string
  last_used?: string
  is_active: boolean
}

export default function ApiKeyManager() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyPermissions, setNewKeyPermissions] = useState<string[]>([])
  const [showKey, setShowKey] = useState<string | null>(null)
  const { getItem, mounted } = useLocalStorageGetter()

  const availablePermissions = [
    'read:market_data',
    'read:company_data',
    'read:portfolio',
    'write:alerts',
    'read:analytics',
    'write:portfolio'
  ]

  useEffect(() => {
    if (mounted) {
      fetchApiKeys()
    }
  }, [mounted])

  const fetchApiKeys = async () => {
    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch('/api/premium/api-keys', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setApiKeys(data.api_keys || [])
      }
    } catch (error) {
      console.error('Error fetching API keys:', error)
    } finally {
      setLoading(false)
    }
  }

  const createApiKey = async () => {
    if (!newKeyName.trim()) return

    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch('/api/premium/api-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: newKeyName,
          permissions: newKeyPermissions
        })
      })

      if (response.ok) {
        const data = await response.json()
        setApiKeys(prev => [...prev, data.api_key])
        setShowCreateForm(false)
        setNewKeyName('')
        setNewKeyPermissions([])
      }
    } catch (error) {
      console.error('Error creating API key:', error)
    }
  }

  const deleteApiKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key?')) return

    try {
      const token = getItem('supabase.auth.token')
      const response = await fetch(`/api/premium/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setApiKeys(prev => prev.filter(key => key.id !== keyId))
      }
    } catch (error) {
      console.error('Error deleting API key:', error)
    }
  }

  const togglePermission = (permission: string) => {
    setNewKeyPermissions(prev =>
      prev.includes(permission)
        ? prev.filter(p => p !== permission)
        : [...prev, permission]
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
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
            API Keys
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Manage your API keys for programmatic access
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
        >
          <PlusIcon className="h-4 w-4" />
          <span>New API Key</span>
        </button>
      </div>

      {showCreateForm && (
        <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Create New API Key
          </h3>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Key Name
              </label>
              <input
                type="text"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                placeholder="e.g., Trading Bot, Mobile App"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Permissions
              </label>
              <div className="grid grid-cols-2 gap-2">
                {availablePermissions.map(permission => (
                  <label key={permission} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={newKeyPermissions.includes(permission)}
                      onChange={() => togglePermission(permission)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {permission}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={createApiKey}
                disabled={!newKeyName.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
              >
                Create Key
              </button>
              <button
                onClick={() => {
                  setShowCreateForm(false)
                  setNewKeyName('')
                  setNewKeyPermissions([])
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
          {apiKeys.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <KeyIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No API keys created yet</p>
              <p className="text-sm mt-1">Create your first API key to get started</p>
            </div>
          ) : (
            apiKeys.map(key => (
              <div key={key.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {key.name}
                      </h3>
                      <span className={`px-2 py-1 text-xs rounded-full ${key.is_active
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                        {key.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {key.key.substring(0, 8)}...
                      </span>
                      <button
                        onClick={() => setShowKey(showKey === key.id ? null : key.id)}
                        className="text-blue-600 hover:text-blue-800 dark:text-blue-400"
                      >
                        {showKey === key.id ? (
                          <EyeSlashIcon className="h-4 w-4" />
                        ) : (
                          <EyeIcon className="h-4 w-4" />
                        )}
                      </button>
                    </div>

                    {showKey === key.id && (
                      <div className="mb-2 p-2 bg-gray-100 dark:bg-gray-700 rounded text-sm font-mono">
                        {key.key}
                      </div>
                    )}

                    <div className="flex flex-wrap gap-1 mb-2">
                      {key.permissions.map(permission => (
                        <span
                          key={permission}
                          className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                        >
                          {permission}
                        </span>
                      ))}
                    </div>

                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Created: {formatDate(key.created_at)}
                      {key.last_used && ` • Last used: ${formatDate(key.last_used)}`}
                    </div>
                  </div>

                  <button
                    onClick={() => deleteApiKey(key.id)}
                    className="text-red-600 hover:text-red-800 dark:text-red-400"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
} 